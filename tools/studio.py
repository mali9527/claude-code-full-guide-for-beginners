#!/usr/bin/env python3
"""The six local, file-based Studio command groups."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
import tempfile
import time
import yaml
from studio_lib.common import StudioError, atomic_write, dump_yaml, git_commit, load_yaml, run_git, safe_path

VERSION = "0.1.0"


def locate(start):
    start = Path(start).resolve()
    for path in [start] + list(start.parents):
        if (path / "workspace.yaml").is_file():
            return path, load_yaml(path / "workspace.yaml")
        if (path / "book.yaml").is_file():
            return path, None
    raise StudioError("当前目录不在总控或作品内；使用 --root 指定目录")


def works(root, workspace, target=None):
    if workspace is None:
        book = load_yaml(root / "book.yaml")
        if target and target != book.get("id"):
            raise StudioError("当前独立作品 ID 不匹配：" + target)
        return [{"id": book.get("id"), "path": ".", "state": "standalone", "is_test": book.get("is_test", False)}]
    registered = workspace.get("works", [])
    if len({w["id"] for w in registered}) != len(registered):
        raise StudioError("workspace.yaml: 重复作品 ID")
    selected = [w for w in registered if not target or w["id"] == target]
    if target and not selected: raise StudioError("未登记作品：" + target)
    return selected


def work_path(root, work):
    path = safe_path(root, work["path"])
    if not (path / "book.yaml").is_file(): raise StudioError(str(path) + ": 缺少 book.yaml")
    book = load_yaml(path / "book.yaml")
    if book.get("id") != work["id"]: raise StudioError(str(path) + ": 登记与 book.yaml 的 ID 不符")
    return path


def task_metadata(path):
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        try: return yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError: return {"state": "invalid"}
    return {}


def status(root, workspace, target):
    started = time.monotonic()
    items = []
    for w in works(root, workspace, target):
        path = work_path(root, w); book = load_yaml(path / "book.yaml")
        facts = load_yaml(path / "facts.yaml") if (path / "facts.yaml").exists() else []
        expired, uncertain = [], []
        for fact in facts or []:
            try:
                day = datetime.date.fromisoformat(str(fact["checked_on"]))
                ttl = fact.get("ttl_days", None if fact.get("category") == "stable" else
                               90 if fact.get("category") in ("price", "quota", "account") else 180)
                if ttl is not None and (datetime.date.today() - day).days >= ttl: expired.append(fact["id"])
            except (KeyError, ValueError, TypeError): uncertain.append(fact.get("id", "?"))
            if fact.get("status") != "confirmed": uncertain.append(fact.get("id", "?"))
        tasks = []
        if workspace:
            p = root / "private" / w["id"] / "tasks.md"
            if p.exists():
                for card in re.split(r"(?m)^## ", p.read_text(encoding="utf-8"))[1:]:
                    title = card.splitlines()[0].strip()
                    state = re.search(r"(?m)^状态[：:]\s*(.+)", card)
                    tasks.append({"id": title, "state": state.group(1).strip() if state else "unknown",
                                  "path": str(p.relative_to(root))})
        reviews = {}
        for p in sorted((path / "checks").glob("*.yaml")):
            value = load_yaml(p)
            for check in value if isinstance(value, list) else [value]:
                if isinstance(check, dict):
                    key = check.get("kind", "unknown") + ":" + check.get("result", "unknown")
                    reviews[key] = reviews.get(key, 0) + 1
        try: head = git_commit(path)
        except StudioError: head = None
        from studio_lib.illustrations import audit
        illustration_state = audit(path)
        items.append({"illustrations": illustration_state, "id": w["id"], "state": w.get("state"), "path": str(path), "source_commit": head,
                      "units": len(book.get("units", [])), "tasks": tasks, "fact_expired": expired,
                      "fact_unknown": sorted(set(uncertain)), "recorded_checks": reviews,
                      "quality": "未重新核对；运行 check 获取当前基线结果",
                      "published": book.get("published", {}), "is_test": w.get("is_test", False)})
    return {"ok": True, "phase": (workspace or {}).get("phase", "standalone"), "works": items,
            "candidates": (workspace or {}).get("candidates", []), "elapsed_seconds": round(time.monotonic()-started, 4),
            "network": "未访问", "build": "未执行"}



def update_roadmap(root, workspace):
    if workspace is None:
        raise StudioError("ROADMAP 仅属于私有总控")
    from studio_lib.builder import region, read_json
    path = root / "ROADMAP.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# 机制路线图\n\n<!-- studio:works -->\n<!-- /studio:works -->\n"
    manifest = root / ".studio" / "roadmap.json"
    previous = read_json(manifest, {})
    rows = ["| 作品 | 状态 | 优先级 | 是否样例 |", "|---|---|---|---|"]
    for item in sorted(workspace.get("works", []), key=lambda w: (w.get("priority",99), w["id"])):
        rows.append("| {} | {} | {} | {} |".format(item["id"],item.get("state","unknown"),
                    item.get("priority","—"),"是" if item.get("is_test") else "否"))
    rows.append("\n候选：" + "、".join(w["id"] for w in workspace.get("candidates", [])) + "。未立项候选不代表已出版。")
    result,digest = region(text,"works","\n".join(rows),previous,"ROADMAP.md#works")
    atomic_write(path,result)
    atomic_write(manifest,json.dumps({"ROADMAP.md#works":digest})+"\n")
    return str(path)


def check(path, publication=False, scope=None, languages=None, freshness=True, source_only=False):
    from studio_lib.checker import check_book
    report = check_book(path, publication=publication, scope=scope, freshness=freshness, source_only=source_only)
    if languages and "zh-TW" in languages:
        from studio_lib.builder import translation_status
        book = load_yaml(path / "book.yaml")
        statuses = translation_status(path, book, scope)
        report["translations"] = statuses
        for item in statuses:
            if item["status"] != "current":
                report["issues"].append({"level": "error" if publication else "warning", "code": "translation_"+item["status"],
                                         "path": "translations.yaml", "message": "{}: {}".format(item["unit"], item["status"])})
        pending_images = [d["id"] for d in book.get("diagrams", []) if d.get("type") == "illustration" and (not scope or d.get("unit") in scope)]
        if pending_images:
            report["issues"].append({"level": "error" if publication else "warning", "code": "illustration_localization_pending",
                                     "path": "book.yaml:diagrams", "message": "繁体正文转换不包含图内文字；待单独本地化：" + ", ".join(pending_images)})
        report["ok"] = not any(i["level"] == "error" for i in report["issues"])
        report["summary"]["errors"] = sum(i["level"]=="error" for i in report["issues"])
        report["summary"]["warnings"] = sum(i["level"]=="warning" for i in report["issues"])
    return report


def install_toolkit(destination, source_tools):
    target = destination / "tools"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("studio.py", "requirements.txt", "package.json", "package-lock.json", "FORMAT.md", "README.md"):
        if (source_tools / name).is_file(): shutil.copy2(source_tools / name, target / name)
    shutil.copytree(source_tools / "studio_lib", target / "studio_lib", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if (source_tools.parent / "standards").is_dir():
        shutil.copytree(source_tools.parent / "standards", target / "standards", dirs_exist_ok=True)
    atomic_write(target / "TOOLKIT_VERSION", VERSION + "\n")
    import hashlib
    manifest = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in target.rglob("*") if p.is_file() and p.name != "toolkit-manifest.json"
                and not {"node_modules", "__pycache__"}.intersection(p.relative_to(target).parts)}
    atomic_write(target / "toolkit-manifest.json", json.dumps({"version": VERSION, "files": manifest}, indent=2)+"\n")


def new_book(root, workspace, args):
    if workspace is None: raise StudioError("new-book 只能在私有总控内使用")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.id): raise StudioError("作品 ID 使用小写字母、数字和连字符")
    if any(w["id"] == args.id for w in workspace.get("works", [])): raise StudioError("作品已登记：" + args.id)
    relative = args.path or "books/" + args.id
    dest = safe_path(root, relative)
    if dest.exists(): raise StudioError("目标已存在，停止覆盖：" + str(dest))
    reserved = {".git", ".agents", ".claude", ".venv", "private", "tools", "standards", "skills", "templates", "commons", "products"}
    if dest.relative_to(root).parts[0] in reserved:
        raise StudioError("作品目录不能位于总控工具、私有记录或 Git 内部")
    for existing in workspace.get("works", []):
        base = safe_path(root, existing["path"]).resolve()
        if base in dest.parents or dest in base.parents:
            raise StudioError("作品目录不能嵌套其他作品")
    template = root / "templates" / ("tutorial" if args.type == "tutorial" else "book")
    if not template.is_dir(): raise StudioError("模板不存在：" + str(template))
    if args.title and ("\n" in args.title or "\r" in args.title): raise StudioError("标题不能包含换行")
    with tempfile.TemporaryDirectory(prefix="studio-new-") as tmp:
        stage = Path(tmp) / args.id
        shutil.copytree(template, stage, symlinks=True)
        for p in stage.rglob("*"):
            if p.is_file() and not p.is_symlink() and p.name != "book.yaml":
                try: text = p.read_text(encoding="utf-8")
                except UnicodeError: continue
                p.write_text(text.replace("__WORK_ID__", args.id).replace("__TITLE__", args.title or args.id), encoding="utf-8")
        book = load_yaml(stage / "book.yaml")
        book["id"] = args.id; book["title"] = args.title or args.id
        book["type"] = args.type; book["is_test"] = args.test
        if book.get("product") == "__WORK_ID__": book["product"] = args.id
        book.setdefault("repository", {})["name"] = args.repo
        dump_yaml(stage / "book.yaml", book)
        install_toolkit(stage, root / "tools")
        if (root / "standards").is_dir():
            shutil.copytree(root / "standards", stage / "tools" / "standards", dirs_exist_ok=True)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, dest, symlinks=True)
    subprocess.run(["git", "init", "-b", "codex/initial", str(dest)], check=True, capture_output=True)
    workspace.setdefault("works", []).append({"id": args.id, "path": relative, "state": "planned", "is_test": args.test, "priority": args.priority})
    dump_yaml(root / "workspace.yaml", workspace)
    return {"ok": True, "target": args.id, "outputs": [str(dest)], "branch": "codex/initial",
            "remote": "未创建、未配置 origin", "pending": ["填入读者承诺、范围与产品基线", "立项后另行安排生产"]}


def commons_diff(root, workspace):
    if workspace is None: raise StudioError("commons diff 需要总控中的底稿库")
    available = {}
    for p in sorted((root / "commons").glob("*/*.md")):
        meta = task_metadata(p)
        if not meta.get("id") or not meta.get("version"): continue
        previous = available.get(meta["id"])
        key = lambda v: tuple(int(n) for n in re.findall(r"\d+", str(v)))
        if previous is None or key(meta["version"]) > key(previous["version"]):
            available[meta["id"]] = meta
    results = []
    for w in works(root, workspace):
        book = load_yaml(work_path(root, w) / "book.yaml")
        for u in book.get("units", []):
            source = u.get("derived_from")
            if not source: continue
            current = available.get(source.get("id"))
            latest = current.get("version") if current else None
            results.append({"work": w["id"], "unit": u["id"], "source": source["id"], "adopted": source.get("version"),
                            "available": latest, "action": "待核对底稿" if not current else
                            ("无需升级" if latest == source.get("version") else "建议建立比较任务；不改正文")})
    return {"ok": True, "comparisons": results, "writes": []}


def source_gate(path, source, scope, languages):
    commit = git_commit(path, source)
    with tempfile.TemporaryDirectory(prefix="studio-gate-") as tmp:
        clone = Path(tmp) / "book"
        r = subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(path), str(clone)], capture_output=True, text=True)
        if r.returncode: raise StudioError("本地来源副本创建失败：" + r.stderr)
        run_git(clone, "checkout", "--quiet", "--detach", commit)
        return check(clone, True, scope, languages), commit


def release_entries(path, plan_path):
    from studio_lib.builder import build_book
    from studio_lib.release import _load_plan
    path = Path(path).resolve()
    plan_path, plan = _load_plan(plan_path)
    receipt_path = plan_path.parent / "receipt.json"
    if not receipt_path.exists(): raise StudioError("缺少公开回执")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("published") is not True or not receipt.get("verified_at"):
        raise StudioError("回执不能证明已核验公开；先执行 resume")
    for key in ("repository", "tag", "commit", "work_id", "kind", "source_version", "scope", "assets"):
        if receipt.get(key) != plan.get(key): raise StudioError("公开回执与发布清单不匹配：" + key)
    execution_path = plan_path.parent / "execution.json"
    if not execution_path.exists() or json.loads(execution_path.read_text(encoding="utf-8")).get("plan") != plan:
        raise StudioError("发布执行记录与清单不匹配；先核对原始记录")
    if plan["promote"] and receipt.get("promotion") != "succeeded":
        raise StudioError("推荐入口更新尚未成功；保留当前入口，先 audit/resume")
    book = load_yaml(path / "book.yaml")
    if book.get("id") != plan["work_id"] or (book.get("repository") or {}).get("name", "").lower() != plan["repository"].lower():
        raise StudioError("书仓与发布清单身份不匹配")

    def version_order(version):
        match = re.fullmatch(r"v(\d{4})\.(\d{2})\.(\d+)(?:-rc\.(\d+))?", str(version))
        if not match: raise StudioError("无法安全比较现有入口版本：" + str(version))
        year, month, edition, candidate = match.groups()
        return (int(year), int(month), int(edition), candidate is None, int(candidate or 0))

    previous = book.get("published") or {}; updated = dict(previous)
    if plan["kind"] == "pdf":
        asset = next(a for a in plan["assets"] if a["name"].lower().endswith(".pdf"))
        current_pdf = previous.get("pdf") or {}
        if current_pdf:
            match = re.fullmatch(r"pdf-(v\d{4}\.\d{2}\.\d+(?:-rc\.\d+)?)-(\d{2,})", str(current_pdf.get("tag")))
            if not match or current_pdf.get("source_version") != match.group(1):
                raise StudioError("现有 PDF 入口无法安全比较；先核对配置")
            old_order = (version_order(match.group(1)), int(match.group(2)))
            new_order = (version_order(plan["source_version"]), int(plan["tag"].rsplit("-", 1)[1]))
            if old_order > new_order: raise StudioError("已有较新 PDF 入口，停止旧导出版覆盖")
            if current_pdf.get("tag") == plan["tag"] and any(current_pdf.get(k) != v for k, v in
                    {"source_commit": plan["commit"], "file": asset["name"]}.items()):
                raise StudioError("现有同名 PDF 入口来源或附件不匹配")
        updated["pdf"] = {"tag": plan["tag"], "source_version": plan["source_version"], "source_commit": plan["commit"],
                          "file": asset["name"], "date": (current_pdf.get("date") if current_pdf.get("tag") == plan["tag"] else None)
                          or str(receipt.get("published_at") or receipt["verified_at"])[:10]}
    else:
        current = previous.get("version")
        if current and version_order(current) > version_order(plan["tag"]):
            raise StudioError("已有较新正文入口，停止旧版本覆盖")
        if current and current != plan["tag"] and current != plan.get("expected_previous"):
            raise StudioError("本地正文入口已变化，停止自动覆盖：" + str(current))
        updated["version"] = plan["tag"]
    old = (path / "book.yaml").read_text(encoding="utf-8")
    book["published"] = updated; dump_yaml(path / "book.yaml", book)
    try:
        build = build_book(path)
        if not build.get("ok"): raise StudioError("入口构建未成功；已保留公开事实")
    except Exception as exc:
        atomic_write(path / "book.yaml", old)
        receipt["entry_update"] = {"status": "failed", "error": str(exc), "date": str(datetime.date.today())}
        atomic_write(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        raise
    receipt["entry_update"] = {"status": "complete", "date": str(datetime.date.today())}
    atomic_write(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return {"ok": True, "published": True, "entries": updated, "build": build, "pending": ["检查入口差异后按授权合入；命令未 push"]}


def release_command(root, workspace, args):
    from studio_lib.release import prepare_release, audit_release, publish_release, resume_release, _load_plan
    if args.action == "prepare":
        selected = works(root, workspace, args.work)
        if len(selected) != 1: raise StudioError("release prepare 必须指定一个作品")
        w = selected[0]; path = work_path(root, w)
        if not args.version: raise StudioError("需要 --version")
        if workspace is None and not args.records: raise StudioError("独立书仓必须 --records 指向书仓外的私有目录")
        commit = git_commit(path, args.source)
        snapshot = yaml.safe_load(run_git(path, "show", commit + ":book.yaml"))
        if not isinstance(snapshot, dict) or snapshot.get("id") != w["id"]:
            raise StudioError("来源提交与登记作品身份不匹配")
        if (workspace or {}).get("phase") == "M" and (not w.get("is_test") or not snapshot.get("is_test")):
            raise StudioError("M 阶段仅允许虚构测试作品，不能准备真实书发行")
        scope = {"units": args.units if args.units is not None else [u["id"] for u in snapshot["units"]],
                 "languages": args.language if args.language is not None else [snapshot.get("language", "zh-CN")]}
        if not scope["units"] or not scope["languages"]: raise StudioError("公开范围不能为空")
        import hashlib
        pdf_reviews = []
        for item in args.asset:
            asset_path = Path(item).resolve()
            if asset_path.suffix.lower() != ".pdf": continue
            export_path = asset_path.parent / "export.json"
            if not export_path.is_file(): raise StudioError("PDF 缺少旁边的 export.json 来源与审阅记录")
            export = json.loads(export_path.read_text(encoding="utf-8"))
            digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
            if export.get("source_commit") != commit or export.get("sha256") != digest or export.get("file") != asset_path.name:
                raise StudioError("PDF 来源提交、文件或 SHA-256 与 export.json 不匹配")
            if export.get("visual_review") != "pass": raise StudioError("PDF 视觉审阅尚未通过；不能准备公开")
            pdf_reviews.append({"file": asset_path.name, "source_commit": commit, "sha256": digest, "visual_review": "pass"})
        gate, checked_commit = source_gate(path, commit, scope["units"], scope["languages"])
        if checked_commit != commit: raise StudioError("门禁核验的来源提交不符")
        gate = {**gate, "commit": commit, "scope": scope, "pdf_reviews": pdf_reviews,
                "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if not gate["ok"]: return {"ok": False, "stage": "publication_gate", "check": gate}
        records = Path(args.records).resolve() if args.records else root / "private" / w["id"] / "releases"
        notes = Path(args.notes_file).read_text(encoding="utf-8") if args.notes_file else ""
        result = prepare_release(path, records, version=args.version, source_ref=commit, assets=args.asset,
                                 title=args.title, notes=notes, kind=args.kind, source_version=args.source_version,
                                 promote=args.promote, expected_previous=args.expected_latest, repository=args.repo, scope=scope)
        frozen = {a["name"]: a["sha256"] for a in result["plan"]["assets"]}
        if any(frozen.get(review["file"]) != review["sha256"] for review in pdf_reviews):
            raise StudioError("PDF 在核验与冻结之间改变；清单未通过门禁，请保留现场核对")
        atomic_write(Path(result["plan_path"]).parent / "gate.json", json.dumps(gate, ensure_ascii=False, indent=2) + "\n")
        return {**result, "pending": ["核对清单与附件；publish 需要显式账号、目标和 --execute"]}
    if not args.plan: raise StudioError("需要 --plan 指向已准备的私有 plan.json")
    if args.action == "audit":
        return audit_release(args.plan, expected_repository=args.repo)
    plan_path, plan = _load_plan(args.plan)
    if args.work and args.work != plan["work_id"]: raise StudioError("显式作品与发布清单不匹配")
    selected = works(root, workspace, plan["work_id"])
    if len(selected) != 1: raise StudioError("必须指定一个已登记作品")
    w = selected[0]; path = work_path(root, w)
    if args.action == "entries":
        return release_entries(path, plan_path)
    if args.action not in ("publish", "resume"): raise StudioError("未知发布动作")
    if not args.repo or not args.account: raise StudioError("执行发布必须明确 --repo owner/repo 与 --account")
    if not args.execute: raise StudioError("执行发布必须显式提供 --execute")
    if args.repo.lower() != plan["repository"].lower(): raise StudioError("显式目标仓库与发布清单不一致")
    current_book = load_yaml(path / "book.yaml")
    snapshot = yaml.safe_load(run_git(path, "show", plan["commit"] + ":book.yaml"))
    if not isinstance(snapshot, dict) or any(
            b.get("id") != plan["work_id"] or (b.get("repository") or {}).get("name", "").lower() != plan["repository"].lower()
            for b in (snapshot, current_book)):
        raise StudioError("登记书仓及来源提交与发布清单身份不匹配")
    if bool(snapshot.get("is_test", False)) != plan["is_test"]:
        raise StudioError("发布清单的测试标记与来源提交不匹配")
    test = args.test or plan["is_test"] or w.get("is_test", False) or (workspace or {}).get("phase") == "M"
    allowed = (workspace or {}).get("test_repositories", [])
    if test and (not plan["is_test"] or plan["repository"].lower() not in {r.lower() for r in allowed}):
        raise StudioError("测试发布必须使用 is_test 来源及 workspace.yaml 明确登记的测试仓")
    known_units = {u["id"] for u in snapshot.get("units", [])}
    primary = snapshot.get("language", "zh-CN")
    translated = ((snapshot.get("outputs") or {}).get("translations") or {})
    known_languages = {primary} | {lang for lang, config in translated.items() if isinstance(config, dict) and config.get("enabled")}
    scope = plan["scope"]
    if not scope["units"] or not set(scope["units"]).issubset(known_units) or not set(scope["languages"]).issubset(known_languages):
        raise StudioError("发布清单的公开范围与来源提交不匹配")
    receipt_path = plan_path.parent / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
    already_public = receipt.get("published") is True and bool(receipt.get("verified_at")) and all(
        receipt.get(key) == plan.get(key) for key in ("repository", "tag", "commit", "work_id", "kind", "source_version", "scope", "assets"))
    # A publish response can be lost before the local receipt proves success.
    # Resume checks remote facts first, so an already-public historical release
    # remains recoverable even when its factual review has since expired.
    if args.action == "resume" and not already_public:
        remote_fact = audit_release(plan_path, expected_repository=args.repo)
        already_public = remote_fact.get("ok") and remote_fact.get("published")
    # Unpublished work must pass today's gate at exactly the frozen commit.
    if not already_public:
        gate_path = plan_path.parent / "gate.json"
        previous_gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
        pdf_reviews = previous_gate.get("pdf_reviews", [])
        for asset in plan["assets"]:
            if not asset["name"].lower().endswith(".pdf"): continue
            if not any(review == {"file": asset["name"], "source_commit": plan["commit"],
                                  "sha256": asset["sha256"], "visual_review": "pass"} for review in pdf_reviews):
                raise StudioError("冻结 PDF 缺少匹配的来源与视觉审阅门禁；重新执行 prepare 核对")
        gate, checked_commit = source_gate(path, plan["commit"], scope["units"], scope["languages"])
        if checked_commit != plan["commit"]: raise StudioError("门禁核验的来源提交不符")
        gate = {**gate, "commit": checked_commit, "scope": scope, "pdf_reviews": pdf_reviews,
                "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        atomic_write(plan_path.parent / "gate.json", json.dumps(gate, ensure_ascii=False, indent=2) + "\n")
        if not gate["ok"]: return {"ok": False, "stage": "publication_gate", "check": gate}
    method = publish_release if args.action == "publish" else resume_release
    return method(plan_path, expected_repository=args.repo, authorized=args.execute, expected_account=args.account,
                  allowed_repositories=allowed, test_mode=test)


def parser():
    p = argparse.ArgumentParser(description="AI 教程工程：本地生产与发布机制")
    p.add_argument("--root", default=".", help="总控或独立作品目录")
    p.add_argument("--json", action="store_true", help="机器可读结果")
    p.add_argument("--version", action="version", version=VERSION)
    subs = p.add_subparsers(dest="command", required=True)
    for name in ("status", "check", "build"):
        q = subs.add_parser(name); q.add_argument("work", nargs="?")
        if name == "status": q.add_argument("--write-roadmap", action="store_true")
        if name == "check":
            q.add_argument("--publication", action="store_true"); q.add_argument("--units", nargs="+")
            q.add_argument("--language", action="append", choices=["zh-CN", "zh-TW"])
        if name == "build":
            q.add_argument("--check", action="store_true"); q.add_argument("--zh-tw", action="store_true")
            q.add_argument("--pdf", action="store_true"); q.add_argument("--source")
            q.add_argument("--version", dest="content_version"); q.add_argument("--export-id")
    i = subs.add_parser("illustrations")
    i.add_argument("action", choices=["status", "pack", "import", "select"])
    i.add_argument("work", nargs="?")
    for option in ("figure", "output", "image", "pack", "revision", "tool", "review"):
        i.add_argument("--" + option)
    i.add_argument("--reference-used", action="store_true")
    n = subs.add_parser("new-book"); n.add_argument("id"); n.add_argument("--title"); n.add_argument("--path")
    n.add_argument("--type", choices=["book", "tutorial"], default="book"); n.add_argument("--repo")
    n.add_argument("--test", action="store_true"); n.add_argument("--priority", type=int, default=3)
    c = subs.add_parser("commons"); c.add_argument("action", choices=["diff"])
    r = subs.add_parser("release")
    r.add_argument("action", choices=["prepare", "audit", "publish", "resume", "entries"]); r.add_argument("work", nargs="?")
    r.add_argument("--plan"); r.add_argument("--repo"); r.add_argument("--account"); r.add_argument("--execute", action="store_true")
    r.add_argument("--test", action="store_true"); r.add_argument("--records"); r.add_argument("--version")
    r.add_argument("--source", default="HEAD"); r.add_argument("--asset", action="append", default=[])
    r.add_argument("--title"); r.add_argument("--notes-file"); r.add_argument("--kind", choices=["milestone","pdf"], default="milestone")
    r.add_argument("--source-version"); r.add_argument("--promote", action="store_true"); r.add_argument("--expected-latest")
    r.add_argument("--units", nargs="+"); r.add_argument("--language", action="append", choices=["zh-CN","zh-TW"])
    return p



def human_result(command, result):
    lines = [("完成" if result.get("ok") else "需要处理") + " · " + command]
    if result.get("published"):
        lines.append("远端已公开；入口等后续步骤以以下结果为准。")
    if "works" in result:
        lines.append("阶段：{}；离线只读，未构建。".format(result.get("phase")))
        for work in result["works"]:
            lines.append("{} · {} · {} 个单元".format(work["id"], work["state"], work["units"]))
            lines.append("  路径：" + work["path"])
            lines.append("  提交：" + str(work.get("source_commit") or "尚未提交"))
            lines.append("  事实过期 {} 项，待核对 {} 项；任务 {} 项。".format(
                len(work["fact_expired"]), len(work["fact_unknown"]), len(work["tasks"])))
            for task in work["tasks"]: lines.append("  - {}：{}".format(task["id"], task["state"]))
            lines.append("  质量：登记概览，请运行 check 核对当前基线。")
        lines.append("耗时：{} 秒。".format(result.get("elapsed_seconds")))
    if "figures" in result:
        lines.append("手绘 {} 张；旧图剩余 {} 张。".format(len(result["figures"]), result["legacy_remaining"]))
        for row in result["figures"]:
            lines.append("{} · {} · {}".format(row["id"], row["stage"], row["source"]))
        for issue in result["issues"]: lines.append(issue["message"])
    reports = result.get("results") or [result]
    for report in reports:
        if "check" in report:
            report = report["check"]
        if "summary" in report:
            summary=report["summary"]
            lines.append("{}：{} 个单元，错误 {}，提示 {}；{}。".format(
                summary.get("book"), summary.get("units"), summary.get("errors"), summary.get("warnings"),
                "已检查公开条件" if summary.get("publication") else "结构检查，未宣称可公开"))
            for issue in report.get("issues", []):
                lines.append("  [{}] {}：{}".format("阻断" if issue["level"]=="error" else "待核对",
                             issue["path"], issue["message"]))
            for unit,quality in summary.get("quality",{}).items():
                lines.append("  {}：{}".format(unit,"；".join("{}={}".format(k,v) for k,v in quality.items())))
        elif report.get("mode") in ("build","check","pdf"):
            lines.append("{} · {} · 来源 {}".format(report.get("target"),report["mode"],report.get("source_commit","当前源稿")))
            for path in report.get("changed",report.get("outputs",[])): lines.append("  " + str(path))
            if report.get("mode")=="check" and report.get("ok"): lines.append("  生成物一致，源仓未写入。")
        else:
            for key,label in (("target","作品"),("repository","仓库"),("tag","标签"),("commit","来源提交"),
                              ("status","状态"),("promotion","推荐入口"),("plan_path","清单"),("receipt_path","回执"),
                              ("branch","分支"),("remote","远端")):
                if key in report: lines.append(label+"："+str(report[key]))
            for item in report.get("comparisons",[]):
                lines.append("{} / {}：底稿 {}，{} → {}；{}".format(item["work"],item["unit"],item["source"],
                             item["adopted"],item["available"],item["action"]))
            for path in report.get("outputs",[]): lines.append("产物："+str(path))
        for item in report.get("pending",[]): lines.append("下一步："+str(item))
    if result.get("roadmap"): lines.append("已更新登记概览："+result["roadmap"])
    return "\n".join(lines)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        root, workspace = locate(args.root)
        if args.command == "status":
            result = status(root, workspace, args.work)
            if args.write_roadmap:
                result["roadmap"] = update_roadmap(root, workspace)
        elif args.command == "illustrations":
            selected = works(root, workspace, args.work)
            if len(selected) != 1: raise StudioError("插图操作必须指定一本书")
            from studio_lib.illustrations import command
            result = command(work_path(root, selected[0]), args)
        elif args.command == "new-book": result = new_book(root, workspace, args)
        elif args.command == "commons": result = commons_diff(root, workspace)
        elif args.command == "release": result = release_command(root, workspace, args)
        else:
            reports = []
            for w in works(root, workspace, args.work):
                path = work_path(root, w)
                if args.command == "check":
                    report = check(path, args.publication, args.units, args.language)
                else:
                    from studio_lib.builder import build_book
                    structure = check(path, freshness=False, source_only=True)
                    if not structure["ok"] and not args.pdf:
                        report = {"ok": False, "stage": "structure", "check": structure}
                    else:
                        report = build_book(path, check_only=args.check, translate=args.zh_tw, pdf=args.pdf,
                                            source_ref=args.source, version=args.content_version, export_id=args.export_id)
                reports.append(report)
            result = {"ok": all(r["ok"] for r in reports), "results": reports}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            print(human_result(args.command, result))
        return 0 if result.get("ok") else 1
    except (StudioError, OSError, ValueError, KeyError, TypeError) as exc:
        error = {"ok": False, "error": str(exc)}
        print(json.dumps(error, ensure_ascii=False) if args.json else "未完成：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
