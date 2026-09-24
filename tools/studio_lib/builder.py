"""Deterministic local outputs, guarded translation, fixed-commit PDF export."""
from pathlib import Path
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from urllib.parse import quote, unquote, urlsplit
import yaml
from .common import StudioError, atomic_write, git_commit, load_yaml, safe_path, slug, stripped_generated

TICK = chr(96)
MANIFEST = ".studio/generated.json"


def sha(value):
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise StudioError("{}: {}".format(path, exc))


def relative_url(target, parent):
    return quote(os.path.relpath(target, parent).replace(os.sep, "/"), safe="/#")


def region(text, name, value, previous, key, check_only=False):
    start, end = "<!-- studio:{} -->".format(name), "<!-- /studio:{} -->".format(name)
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise StudioError("{}: 需要恰好一组 {} / {} 受管标记".format(key, start, end))
    left, rest = text.split(start, 1)
    old, right = rest.split(end, 1)
    new = "\n" + value.strip() + "\n"
    old_sha = previous.get(key)
    if not check_only and old != new:
        if old_sha and sha(old) != old_sha:
            raise StudioError("{}: 受管区域有人工改动，保留现场；先比较并合并".format(key))
        if not old_sha and old.strip():
            raise StudioError("{}: 首次接管遇到非空区域，请人工确认内容后清空标记内部".format(key))
    return left + start + new + end + right, sha(new)


def book_inputs(root):
    book = load_yaml(root / "book.yaml")
    if not isinstance(book, dict) or not isinstance(book.get("units"), list) or not book["units"]:
        raise StudioError("book.yaml: 需要非空 units 清单")
    bodies, ids, paths = {}, set(), set()
    for unit in book["units"]:
        if not isinstance(unit, dict) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", unit.get("id", "")):
            raise StudioError("book.yaml: 无效单元 ID")
        uid, path = unit["id"], unit.get("path")
        if uid in ids or path in paths:
            raise StudioError("book.yaml: 重复单元 ID 或路径")
        ids.add(uid); paths.add(path)
        p = safe_path(root, path)
        try:
            bodies[uid] = p.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise StudioError("{}: {}".format(path, exc))
    return book, bodies


def map_markdown(text, transform):
    """Apply a line transform outside both CommonMark fence forms."""
    lines, fence, length = [], None, 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(" + TICK + r"{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence, length = token[0], len(token)
            elif token[0] == fence and len(token) >= length and not line[marker.end():].strip():
                fence = None
            lines.append(line); continue
        lines.append(line if fence else transform(line))
    return "".join(lines)


def map_inline(text, transform):
    pattern = "(" + TICK + r"+[^" + TICK + r"\n]*" + TICK + "+)"
    return "".join(part if i % 2 else transform(part) for i, part in enumerate(re.split(pattern, text)))


def headings(text):
    result, seen = {}, {}
    def line(s):
        m = re.match(r"^#{1,6}\s+(.+)", s)
        if m:
            key = slug(m.group(1)); n = seen.get(key, 0); seen[key] = n + 1
            anchor = key + ("-" + str(n) if n else "")
            result[anchor] = anchor
        return s
    map_markdown(text, line)
    return result


def rewritten_body(root, unit, text, out_parent, units, pdf_mode=False, source_commit=None):
    path_to_unit = {safe_path(root, u["path"]).resolve(): u for u in units}
    heading_ids = {u["id"]: headings(safe_path(root, u["path"]).read_text(encoding="utf-8")) for u in units}
    counters = {}
    def links(s):
        def link(m):
            dest = m.group(2)
            if urlsplit(dest).scheme or dest.startswith("//"): return m.group(0)
            path, mark, fragment = dest.partition("#")
            source = safe_path(root, unit["path"])
            target = (source.parent / unquote(path)).resolve() if path else source.resolve()
            if target in path_to_unit and not m.group(1).startswith("!"):
                u = path_to_unit[target]
                anchor = u["id"] + "-" + unquote(fragment) if fragment else u["id"]
                new = "#" + anchor
            else:
                try: target.relative_to(root.resolve())
                except ValueError: raise StudioError("{}: 链接越界 {}".format(unit["path"], dest))
                new = relative_url(target, out_parent) + (mark + fragment if mark else "")
                if pdf_mode and source_commit and not m.group(1).startswith("!"):
                    repo = (load_yaml(root / "book.yaml").get("repository") or {}).get("name")
                    if repo:
                        new = "https://github.com/" + repo + "/blob/" + source_commit + "/" + quote(target.relative_to(root.resolve()).as_posix(), safe="/") + (mark + fragment if mark else "")
            return m.group(1) + "(" + new + ")"
        return re.sub(r"(!?\[[^\]\n]*\])\(([^)\s]+)\)", link, s)
    def line(s):
        m = re.match(r"^(#{1,6})\s+(.+?)(\n?)$", s)
        body = map_inline(s, links)
        if not m: return body
        key = slug(m.group(2)); n = counters.get(key, 0); counters[key] = n + 1
        anchor = unit["id"] + "-" + key + ("-" + str(n) if n else "")
        if pdf_mode:
            body = body.rstrip("\n") + " {#" + anchor + "}\n"
        else:
            body = '<a id="{}"></a>\n{}'.format(anchor, body)
        return body
    result = map_markdown(stripped_generated(text), line)
    if pdf_mode:
        # A unit-level target is stable even after its visible heading changes.
        result = "[]{#" + unit["id"] + "}\n\n" + result
    return result


def release_text(book):
    published = book.get("published") or {}
    repo = (book.get("repository") or {}).get("name")
    version = published.get("version")
    lines = ["当前维护稿以本仓库为准。"]
    if version and repo:
        lines.append("已公开正文：[{}](https://github.com/{}/releases/tag/{})。".format(version, repo, version))
    else:
        lines.append("尚未登记已公开的里程碑版本。")
    pdf = published.get("pdf")
    if isinstance(pdf, dict) and repo:
        lines.append("PDF 对应正文 {}，导出版 [{}](https://github.com/{}/releases/tag/{})；当前正文可能更新。".format(
            pdf.get("source_version"), pdf.get("tag"), repo, pdf.get("tag")))
    return "\n\n".join(lines)


def translated_text(text, terms):
    try:
        from opencc import OpenCC
    except ImportError:
        raise StudioError("繁体依赖缺失；安装 tools/requirements.txt 后重试 --zh-tw")
    converter = OpenCC("s2twp")
    protected = r"(\]\([^)]+\)|<[^>]+>"
    if terms:
        protected += "|" + "|".join(re.escape(x) for x in sorted(terms, key=len, reverse=True) if x)
    protected += ")"
    def convert(s):
        return "".join(part if i % 2 else converter.convert(part) for i, part in enumerate(re.split(protected, s)))
    return map_markdown(text, lambda line: map_inline(line, convert))


def translation_links(root, unit, text, units, base):
    source = safe_path(root, unit["path"])
    out = safe_path(root, str(Path(base) / unit["path"]))
    targets = {safe_path(root, u["path"]).resolve(): safe_path(root, str(Path(base)/u["path"])) for u in units}
    counters = {}
    def links(s):
        def link(m):
            dest = m.group(2)
            if urlsplit(dest).scheme or dest.startswith("//"): return m.group(0)
            path, mark, fragment = dest.partition("#")
            if not path: return m.group(0)
            target = (source.parent / unquote(path)).resolve()
            try: target.relative_to(root.resolve())
            except ValueError: raise StudioError("译文链接越界：" + dest)
            translated_target = targets.get(target, target)
            new = relative_url(translated_target, out.parent) + (mark + fragment if mark else "")
            return m.group(1) + "(" + new + ")"
        return re.sub(r"(!?\[[^\]\n]*\])\(([^)\s]+)\)", link, s)
    def line(s):
        m = re.match(r"^#{1,6}\s+(.+)", s)
        body = map_inline(s, links)
        if m:
            key = slug(m.group(1)); n = counters.get(key, 0); counters[key] = n + 1
            anchor = key + ("-" + str(n) if n else "")
            body = '<a id="{}"></a>\n{}'.format(anchor, body)
        return body
    return map_markdown(text, line)


def translation_outputs(root, book, bodies):
    config = ((book.get("outputs") or {}).get("translations") or {}).get("zh-TW") or {}
    if not config.get("enabled"):
        raise StudioError("book.yaml: 未启用 zh-TW")
    base = config.get("directory", "zh-TW")
    safe_path(root, base)
    metadata = load_yaml(root / "translations.yaml") if (root / "translations.yaml").exists() else {"entries": []}
    if not isinstance(metadata, dict) or not isinstance(metadata.get("entries"), list):
        raise StudioError("translations.yaml: 需要 entries 列表")
    old = {(e["unit"], e.get("language")): e for e in metadata["entries"]}
    overrides = load_yaml(root / "translation-overrides.yaml") if (root / "translation-overrides.yaml").exists() else []
    if not isinstance(overrides, list):
        raise StudioError("translation-overrides.yaml: 需要列表")
    unknown = [p.get("unit") for p in overrides if p.get("unit") not in bodies or p.get("language") != "zh-TW"]
    if unknown:
        raise StudioError("translation-overrides.yaml: 未匹配单元或语言 {}".format(unknown))
    try: commit = git_commit(root)
    except StudioError: raise StudioError("繁体生成需要已提交原稿；先在工作分支保存源稿")
    entries, outputs = [], {}
    for unit in book["units"]:
        uid = unit["id"]
        source = stripped_generated(bodies[uid])
        old_source = subprocess.run(["git", "-C", str(root), "show", commit + ":" + unit["path"]],
                                    capture_output=True, text=True)
        if old_source.returncode or stripped_generated(old_source.stdout) != source:
            raise StudioError("{}: 原稿尚未提交，繁体来源无法绑定".format(unit["path"]))
        rel = str(Path(base) / unit["path"])
        target = safe_path(root, rel)
        previous = old.get((uid, "zh-TW"))
        if target.exists() and (not previous or sha(target.read_bytes()) != previous.get("output_sha256")):
            raise StudioError("{}: 发现未登记的人工修改；保留文件并先整理 translation-overrides.yaml".format(rel))
        linked = translation_links(root, unit, source, book["units"], base)
        result = translated_text(linked, book.get("protected_terms", [])) + "\n"
        for patch in overrides:
            if patch["unit"] != uid: continue
            expected, replacement = patch.get("expected"), patch.get("replacement")
            anchor = patch.get("anchor", "")
            if not isinstance(expected, str) or not expected or not isinstance(replacement, str):
                raise StudioError("translation-overrides.yaml: 每项需要非空 expected 与 replacement")
            if anchor and result.count(anchor) != 1:
                raise StudioError("{}: 修订定位 anchor 不唯一或不存在".format(uid))
            pos = result.index(anchor) if anchor else 0
            tail = result[pos:]
            if tail.count(expected) != 1:
                raise StudioError("{}: 人工修订 expected 匹配数量应为 1，实际 {}".format(uid, tail.count(expected)))
            result = result[:pos] + tail.replace(expected, replacement, 1)
        digest = sha(source)
        policy_sha = sha(json.dumps({"patches":[p for p in overrides if p["unit"]==uid],
                                    "protected_terms":book.get("protected_terms",[])},ensure_ascii=False,sort_keys=True))
        same = (previous and previous.get("source_sha256") == digest and previous.get("output_sha256") == sha(result)
                and previous.get("policy_sha256") == policy_sha and previous.get("converter") == "opencc-s2twp/0.1.7")
        if same:
            try:
                previous_commit = git_commit(root, previous.get("source_commit"))
                previous_source = subprocess.run(["git","-C",str(root),"show",previous_commit+":"+unit["path"]],
                                                 capture_output=True,text=True)
                if previous_source.returncode or stripped_generated(previous_source.stdout) != source:
                    same = False
            except StudioError:
                same = False
        entries.append({"unit": uid, "language": "zh-TW", "path": rel,
                        "source_commit": previous["source_commit"] if same else commit,
                        "source_sha256": digest, "converter": "opencc-s2twp/0.1.7",
                        "output_sha256": sha(result), "policy_sha256": policy_sha, "review": previous.get("review", "pending") if same else "pending"})
        outputs[rel] = result
    metadata["entries"] = [e for e in metadata["entries"] if e.get("language") != "zh-TW"] + entries
    outputs["translations.yaml"] = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
    return outputs


def translation_status(root, book, scope=None):
    root = Path(root)
    selected = [u for u in book["units"] if not scope or u["id"] in scope]
    config = ((book.get("outputs") or {}).get("translations") or {}).get("zh-TW") or {}
    if not config.get("enabled"): return [{"unit":u["id"],"status":"disabled"} for u in selected]
    path = root / "translations.yaml"
    if not path.exists(): return [{"unit":u["id"],"status":"missing"} for u in selected]
    meta = load_yaml(path) or {}
    entries = {(e.get("unit"),e.get("language")):e for e in meta.get("entries",[])}
    patches = load_yaml(root/"translation-overrides.yaml") if (root/"translation-overrides.yaml").exists() else []
    if not isinstance(patches,list): raise StudioError("translation-overrides.yaml: 需要列表")
    statuses = []
    for u in selected:
        entry = entries.get((u["id"],"zh-TW"))
        state = "missing"
        if entry:
            source = stripped_generated(safe_path(root,u["path"]).read_text(encoding="utf-8"))
            expected = str(Path(config.get("directory","zh-TW"))/u["path"])
            target = safe_path(root,entry["path"])
            policy = sha(json.dumps({"patches":[p for p in patches if p.get("unit")==u["id"]],
                                    "protected_terms":book.get("protected_terms",[])},ensure_ascii=False,sort_keys=True))
            state = "current"
            if entry.get("path") != expected or entry.get("converter") != "opencc-s2twp/0.1.7": state = "configuration_changed"
            elif entry.get("source_sha256") != sha(source): state = "stale"
            elif entry.get("policy_sha256") != policy: state = "rules_changed"
            elif not target.is_file() or sha(target.read_bytes()) != entry.get("output_sha256"): state = "modified"
            else:
                try:
                    commit = git_commit(root,entry.get("source_commit"))
                    from .common import run_git
                    run_git(root,"merge-base","--is-ancestor",commit,"HEAD")
                    old = run_git(root,"show",commit+":"+u["path"])
                    if stripped_generated(old) != source: state = "source_mismatch"
                except StudioError: state = "source_unavailable"
                if state == "current" and entry.get("review") != "pass": state = "review_pending"
        statuses.append({"unit":u["id"],"status":state})
    return statuses


def build_book(book_dir, check_only=False, translate=False, pdf=False, source_ref=None, version=None, export_id=None):
    root = Path(book_dir).resolve()
    if pdf:
        if check_only: raise StudioError("--check 不能与 --pdf 同用；PDF 单独按固定提交导出")
        return export_pdf(root, source_ref, version, export_id)
    from .checker import check_book
    validation = check_book(root, freshness=False, source_only=True)
    errors = [i for i in validation["issues"] if i["level"] == "error"]
    if errors:
        raise StudioError("构建输入检查失败：" + json.dumps(errors, ensure_ascii=False))
    book, bodies = book_inputs(root)
    outputs, hashes = {}, {}
    old_manifest = read_json(safe_path(root, MANIFEST), {"regions": {}, "files": {}})
    previous = old_manifest.get("regions", {})
    units = book["units"]; config = book.get("outputs") or {}
    source_paths = {u["path"] for u in units}
    readme_rel = config.get("readme", "README.md")
    combined_rel = config.get("combined")
    if readme_rel in source_paths or combined_rel in source_paths or combined_rel == readme_rel:
        raise StudioError("book.yaml: 生成物不得覆盖源稿或相互重叠")
    for i, unit in enumerate(units):
        parent = safe_path(root, unit["path"]).parent
        nav = []
        if i: nav.append("← [{}]({})".format(units[i-1]["title"], relative_url(safe_path(root, units[i-1]["path"]), parent)))
        nav.append("[目录]({})".format(relative_url(safe_path(root, readme_rel), parent)))
        if i+1 < len(units): nav.append("[{}]({}) →".format(units[i+1]["title"], relative_url(safe_path(root, units[i+1]["path"]), parent)))
        key = unit["path"] + "#nav"
        outputs[unit["path"]], hashes[key] = region(bodies[unit["id"]], "nav", " · ".join(nav), previous, key, check_only)
    readme = safe_path(root, readme_rel)
    if not readme.is_file(): raise StudioError("{}: README 不存在".format(readme_rel))
    toc = ["共 {} 个单元，{} 张图。".format(len(units), len(book.get("diagrams") or [])), ""]
    toc += ["{}. [{}]({})".format(i+1, u["title"], relative_url(safe_path(root, u["path"]), readme.parent)) for i, u in enumerate(units)]
    text, hashes[readme_rel+"#toc"] = region(readme.read_text(encoding="utf-8"), "toc", "\n".join(toc), previous, readme_rel+"#toc", check_only)
    text, hashes[readme_rel+"#release"] = region(text, "release", release_text(book), previous, readme_rel+"#release", check_only)
    outputs[readme_rel] = text
    whole = {}
    if combined_rel:
        combined = safe_path(root, combined_rel)
        chunks = ["<!-- Generated by studio; edit the units in book.yaml. -->", "# " + book["title"], "## 目录",
                  "\n".join("- [{}](#{})".format(u["title"], u["id"]) for u in units)]
        for u in units:
            chunks += ['<a id="{}"></a>'.format(u["id"]), rewritten_body(root, u, bodies[u["id"]], combined.parent, units)]
        outputs[combined_rel] = "\n\n".join(chunks) + "\n"
        if not check_only and combined.exists() and combined.read_text(encoding="utf-8") != outputs[combined_rel]:
            old_hash = old_manifest.get("files", {}).get(combined_rel)
            if not old_hash or old_hash != sha(combined.read_bytes()):
                raise StudioError("{}: 合订稿有未登记修改或尚未接管，保留现场".format(combined_rel))
        whole[combined_rel] = sha(outputs[combined_rel])
    if translate:
        translations = translation_outputs(root, book, bodies)
        for path in translations:
            if path in outputs: raise StudioError("{}: 译文与其他输出重叠".format(path))
        outputs.update(translations)
    manifest = json.dumps({"version": 1, "regions": hashes, "files": whole}, ensure_ascii=False, indent=2) + "\n"
    outputs[MANIFEST] = manifest
    changed = [rel for rel, text in outputs.items() if not safe_path(root, rel).exists() or safe_path(root, rel).read_text(encoding="utf-8") != text]
    # No input writes until every output and protected region has passed validation.
    if not check_only:
        with tempfile.TemporaryDirectory(prefix="studio-build-") as tmp:
            stage = Path(tmp)
            for rel, text in outputs.items():
                target = safe_path(stage, rel); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(text, encoding="utf-8")
            for rel in changed:
                atomic_write(safe_path(root, rel), safe_path(stage, rel).read_text(encoding="utf-8"))
    return {"ok": not changed if check_only else True, "target": book["id"], "mode": "check" if check_only else "build",
            "changed": changed, "outputs": list(outputs), "pending": ["繁体审读"] if translate else []}


def tool_run(args, cwd=None):
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StudioError("{}: {}".format(args[0], exc))
    if result.returncode:
        raise StudioError("{} 失败：{}".format(args[0], (result.stderr or result.stdout)[-3000:]))
    return result.stdout.strip()


def export_pdf(root, source_ref, version, export_id):
    if not source_ref or not version or not export_id:
        raise StudioError("PDF 需要 --source、--version 和 --export-id；不得隐式使用工作区")
    if not re.fullmatch(r"v\d{4}\.\d{2}\.\d+(?:-rc\.\d+)?", version) or not re.fullmatch(r"\d{2,}", export_id):
        raise StudioError("无效正文版本或导出编号")
    commit = git_commit(root, source_ref)
    known_tag = subprocess.run(["git","-C",str(root),"rev-parse","--verify","refs/tags/"+version+"^{commit}"],
                               capture_output=True,text=True)
    if known_tag.returncode == 0 and known_tag.stdout.strip() != commit:
        raise StudioError("正文版本标签与 PDF 来源提交不一致：" + version)
    archive = subprocess.run(["git", "-C", str(root), "archive", commit], capture_output=True)
    if archive.returncode: raise StudioError("Git snapshot 获取失败")
    for tool in ("pandoc", "typst"):
        if not shutil.which(tool): raise StudioError("PDF 依赖缺失：" + tool)
    with tempfile.TemporaryDirectory(prefix="studio-pdf-") as tmp:
        stage = Path(tmp); source = stage / "source"; source.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            for member in tar.getmembers():
                safe_path(source, member.name)
                if member.issym() or member.islnk(): raise StudioError("PDF snapshot 不接受符号链接：" + member.name)
            tar.extractall(source)
        book, bodies = book_inputs(source)
        from .checker import check_book
        structure = check_book(source, freshness=False)
        problems = [i for i in structure["issues"] if i["level"] == "error"]
        if problems:
            raise StudioError("PDF 来源结构检查失败：" + json.dumps(problems, ensure_ascii=False))
        pdf_config = (book.get("outputs") or {}).get("pdf") or {}
        if not pdf_config.get("enabled"): raise StudioError("该来源版本未启用 PDF")
        font = pdf_config.get("font", "PingFang SC")
        fonts = tool_run(["typst", "fonts"])
        if font.lower() not in fonts.lower(): raise StudioError("缺少声明的中文字体：" + font)
        parts = ["九月修订稿 · 供阅读与审校。真实账号与完整平台操作尚待完成；跨引擎审核由作者手动选用。", "来源提交：" + TICK + commit + TICK]
        diagram_count = 0
        diagram_pages = []
        for unit in book["units"]:
            body = rewritten_body(source, unit, bodies[unit["id"]], source, book["units"], pdf_mode=True, source_commit=commit)
            pattern = r"<!--\s*diagram:\s*([A-Za-z0-9_-]+)\s*-->\s*" + TICK + r"{3}mermaid\s*\n([\s\S]*?)" + TICK + r"{3}"
            def diagram(match):
                nonlocal diagram_count
                did, code = match.group(1), match.group(2)
                if not any(d.get("id") == did and d.get("unit") == unit["id"] for d in book.get("diagrams", [])):
                    raise StudioError("{}: 未登记的图 {}".format(unit["path"], did))
                mmdc = os.environ.get("STUDIO_MMDC") or shutil.which("mmdc")
                if not mmdc:
                    local = root / "tools" / "node_modules" / ".bin" / "mmdc"
                    mmdc = str(local) if local.exists() else None
                if not mmdc: raise StudioError("图渲染依赖缺失：按 tools/README.md 的 PDF 说明安装 mmdc")
                diagram_count += 1
                inp = source / ("diagram-" + did + ".mmd")
                out = source / ("diagram-" + did + ".png")
                if not code.lstrip().startswith("---"):
                    code = "---\nconfig:\n  theme: forest\n  themeVariables:\n    fontFamily: PingFang SC\n    fontSize: 17px\n    lineColor: '#D9D9D9'\n---\n" + code
                inp.write_text(code, encoding="utf-8")
                args = [mmdc, "-i", str(inp), "-o", str(out), "-b", "white", "-s", "2", "-C", str(source / "tools/pdf-mermaid.css")]
                chrome = os.environ.get("STUDIO_CHROME")
                if chrome:
                    p = source / "puppeteer.json"
                    p.write_text(json.dumps({"executablePath": chrome}), encoding="utf-8")
                    args += ["-p", str(p)]
                tool_run(args, source)
                if not out.is_file() or out.stat().st_size < 20: raise StudioError("图渲染未产生有效文件：" + did)
                diagram_pages.append((did, out.name, unit["id"], unit["title"]))
                return "![{}]({}){{width=100%}}\n\n[查看独立大图页](#pdf-diagram-{})".format(did, out.name, did)
            body = re.sub(pattern, diagram, body)
            from .illustrations import pdf_assets
            body, raster_entries = pdf_assets(source, unit, body, book)
            diagram_count += len(raster_entries)
            diagram_pages.extend(raster_entries)
            for did, filename, _, _ in raster_entries:
                body = body.replace("](" + filename + "){width=100%}", "](" + filename + "){width=100%}\n\n[查看独立大图页](#pdf-diagram-" + did + ")")
            if re.search(TICK+r"{3}mermaid", body): raise StudioError(unit["path"] + ": 存在无登记标记的 Mermaid 图")
            if re.search(r"!\[[^\]]*\]\(https?://", body): raise StudioError("PDF 必须使用已保存的本地图片，不能构建时下载")
            if book.get("type") == "book":
                parts.append(TICK*3 + "{=typst}\n#pagebreak(weak: true)\n" + TICK*3)
            parts.append(body)
        # Wider diagram pages keep the A5 reading text while making dense maps legible.
        if diagram_pages:
            parts.append(TICK*3 + '{=typst}\n#pagebreak(weak: true)\n#set page(paper: "a4", flipped: true, margin: 18mm)\n' + TICK*3)
            for did, filename, uid, title in diagram_pages:
                gallery = '#pagebreak(weak: true)\n'
                gallery += '#text(size: 14pt, weight: "bold", '+json.dumps("图解 "+did+" · "+title, ensure_ascii=False)+') <pdf-diagram-'+did+'>\n'
                gallery += '#v(4mm)\n#block(width: 100%, height: 135mm)[#align(center + horizon)[#image('+json.dumps(filename)+', width: 100%, height: 100%, fit: "contain")]]\n'
                gallery += '#v(3mm)\n#link(<'+uid+'>)[返回本章]\n'
                parts.append(TICK*3 + '{=typst}\n'+gallery+TICK*3)
        markdown = source / "export.md"; markdown.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        # Retain reproducible layout inputs for visual QA without rerendering diagrams.
        diagnostics = safe_path(root, "build/pdf-work/{}/{}".format(version, export_id))
        diagnostics.mkdir(parents=True, exist_ok=True)
        for item in [markdown, source / "tools/pdf-layout.typ"] + list(source.glob("diagram-*.png")):
            shutil.copy2(item, diagnostics / item.name)
        result_pdf = source / (book["id"] + "-" + version + "-" + export_id + ".pdf")
        tool_run(["pandoc", str(markdown), "--from=markdown+raw_html+raw_attribute-citations", "--pdf-engine=typst", "--toc", "--toc-depth=2",
                  "--include-in-header="+str(source / "tools/pdf-layout.typ"),
                  "-V", "page-numbering=1", "-V", "codefont=Sarasa Mono SC",
                  "-V", "mainfont="+font, "-V", "papersize="+pdf_config.get("paper", "a5"),
                  "-V", "fontsize=10pt", "--variable-json=margin:"+json.dumps({"top":"18mm","right":"18mm","bottom":"18mm","left":"18mm"}),
                  "--metadata=title:"+book["title"], "--metadata=author:马力", "--metadata=subtitle:正文 "+version+" · 导出 "+export_id,
                  "--metadata=date:"+str(datetime.date.today()), "--metadata=lang:zh", "--metadata=region:CN",
                  "-o", str(result_pdf)], source)
        if not result_pdf.is_file() or result_pdf.read_bytes()[:5] != b"%PDF-": raise StudioError("未产生有效 PDF")
        output_dir = safe_path(root, "build/pdf/{}/{}".format(version, export_id))
        receipt = {"source_commit": commit, "version": version, "export_id": export_id, "sha256": sha(result_pdf.read_bytes()),
                   "file": result_pdf.name, "font": font, "diagrams": diagram_count,
                   "toolkit_version": book.get("toolkit"), "builder_sha256": sha(Path(__file__).read_bytes()),
                   "layout_sha256": sha((source / "tools/pdf-layout.typ").read_bytes()),
                   "diagram_css_sha256": sha((source / "tools/pdf-mermaid.css").read_bytes()),
                   "tools": {t: tool_run([t, "--version"]).splitlines()[0] for t in ("pandoc", "typst")}, "visual_review": "pending"}
        if output_dir.exists():
            raise StudioError("{}: 导出编号已存在，保留已审阅文件；使用新编号".format(output_dir))
        output_dir.mkdir(parents=True)
        shutil.copy2(result_pdf, output_dir / result_pdf.name)
        atomic_write(output_dir / "export.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        return {"ok": True, "target": book["id"], "mode": "pdf", "source_commit": commit,
                "outputs": [str(output_dir / result_pdf.name), str(output_dir / "export.json")], "pending": ["PDF 视觉审阅"]}
