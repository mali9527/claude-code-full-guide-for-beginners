"""Read-only book checks. Public summaries are declarations, not proof of experiments."""
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit
import os
import re
import yaml

from .common import StudioError, load_yaml, safe_path, run_git, git_commit, slug, stripped_generated

BOOK_FIELDS = set("id title type language product audience baseline repository is_test watershed units outputs diagrams toolkit published platforms required_checks protected_terms".split())
UNIT_FIELDS = set("id title path section depth prerequisites features facts derived_from required_checks".split())
FACT_FIELDS = set("id claim scope sources checked_on category ttl_days status critical".split())
RECORD_FIELDS = set("unit source_commit paths kind result checked_on engine author_engine platforms limitations reason".split())
KINDS = {"editorial", "facts", "operations", "trial"}
CATEGORIES = {"price", "quota", "account", "install", "startup", "permission", "undo", "stable"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "build"}
DIAGRAM = re.compile(r"<!--\s*diagram:\s*([^\s>]+)\s*-->")
LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>\n]+>|(?:\\.|[^()\s]|\([^)]*\))+)(?:\s+['\"][^\n]*?['\"])?\)")
REFERENCE = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", re.M)

# Deliberately small deny-list: recognizable credentials, not a general secret scanner.
TOKEN = re.compile(r"(?:\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b|\bsk-(?:proj-|svcacct-|ant-)?[A-Za-z0-9_-]{20,}\b|\bxox[baprs]-[A-Za-z0-9-]{20,}\b)")
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")


def _redacted(value):
    if isinstance(value, str):
        return TOKEN.sub("[REDACTED]", value)
    if isinstance(value, list):
        return [_redacted(v) for v in value]
    if isinstance(value, dict):
        return {_redacted(k): _redacted(v) for k, v in value.items()}
    return value


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError("日期必须是 YYYY-MM-DD")


def _without_code(text, inline=True):
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"`[^`\n]*`", "", "\n".join(lines)) if inline else "\n".join(lines)


def _anchors(text):
    text = _without_code(text, inline=False)
    anchors, seen = set(), {}
    for line in text.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not m:
            continue
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", m.group(1))
        key = slug(heading)
        count = seen.get(key, 0)
        seen[key] = count + 1
        anchors.add(key if count == 0 else "{}-{}".format(key, count))
    for m in re.finditer(r"(?:id|name)\s*=\s*['\"]([^'\"]+)['\"]", text, re.I):
        anchors.add(m.group(1))
    return anchors


class _Checker:
    def __init__(self, root, publication, scope, today):
        self.root = Path(root).resolve()
        self.publication = publication
        self.scope_requested = scope
        self.today = _date(today) if today is not None else date.today()
        self.issues = []
        self.book, self.units, self.facts, self.texts = {}, {}, {}, {}
        self.scope, self.records, self.quality = set(), [], {}
        self.old_cache = {}
        self.unit_required = {}

    def issue(self, code, path, message, level="error"):
        self.issues.append({"level": level, "code": code, "path": _redacted(str(path)), "message": _redacted(message)})

    def quality_issue(self, code, path, message, unit=None, critical=True):
        selected = unit is None or unit in self.scope
        level = "error" if self.publication and selected and critical else "warning"
        self.issue(code, path, message, level)

    def fields(self, obj, allowed, path, required=()):
        if not isinstance(obj, dict):
            self.issue("invalid_type", path, "必须是映射")
            return False
        for field in obj:
            if field not in allowed:
                self.issue("unknown_field", path, "未知字段：{}".format(field))
        for field in required:
            if field not in obj:
                self.issue("missing_field", path, "缺少字段：{}".format(field))
        return True

    def strings(self, value, path):
        if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
            self.issue("invalid_type", path, "必须是非空字符串列表（允许列表为空）")
            return []
        if len(set(value)) != len(value):
            self.issue("duplicate_reference", path, "列表中有重复引用")
        return value

    def path(self, relative, must_exist=False):
        try:
            p = safe_path(self.root, relative)
            if ".git" in Path(relative).parts or p.resolve() == self.root:
                raise StudioError("不能使用书仓根目录或 Git 内部路径")
            if must_exist and not p.is_file():
                raise StudioError("文件不存在或尚未下载：{}".format(relative))
            return p
        except (StudioError, OSError, ValueError) as exc:
            self.issue("unsafe_or_missing_path", relative, str(exc))
            return None

    def read_yaml(self, relative, default=None):
        p = self.path(relative, True)
        if p is None:
            return default
        try:
            return load_yaml(p)
        except StudioError as exc:
            self.issue("invalid_yaml", relative, str(exc))
            return default

    def check_date(self, value, path, field="checked_on"):
        try:
            d = _date(value)
            if d > self.today:
                self.issue("future_verification", path, "{} 在未来，不能视为核验记录".format(field))
                return None
            return d
        except (ValueError, TypeError):
            self.issue("invalid_date", path, "{} 必须是 YYYY-MM-DD".format(field))
            return None

    def configuration(self):
        book = self.read_yaml("book.yaml", {})
        if not self.fields(book, BOOK_FIELDS, "book.yaml", ("id", "title", "type", "language", "product", "units", "outputs")):
            return
        self.book = book
        for key in ("id", "product"):
            if not isinstance(book.get(key), str) or not SLUG.fullmatch(book.get(key, "")):
                self.issue("invalid_id", "book.yaml", "{} 必须是稳定 slug".format(key))
        for key in ("title", "language"):
            if not isinstance(book.get(key), str) or not book.get(key):
                self.issue("invalid_type", "book.yaml", "{} 必须是非空字符串".format(key))
        if not isinstance(book.get("type"), str) or book.get("type") not in {"book", "tutorial"}:
            self.issue("invalid_type", "book.yaml", "type 必须是 book 或 tutorial")
        if "is_test" in book and not isinstance(book["is_test"], bool):
            self.issue("invalid_type", "book.yaml", "is_test 必须是布尔值")
        for name, fields in (("baseline", {"product_version", "checked_on"}), ("repository", {"name", "default_branch"}), ("published", {"version", "pdf"})):
            if name in book and book[name] is not None:
                self.fields(book[name], fields, "book.yaml:" + name)
        if isinstance(book.get("baseline"), dict) and book["baseline"].get("checked_on"):
            self.check_date(book["baseline"]["checked_on"], "book.yaml:baseline")
        checks = self.strings(book.get("required_checks", ["editorial", "facts", "operations"]), "book.yaml:required_checks")
        if set(checks) - KINDS:
            self.issue("invalid_check_kind", "book.yaml", "required_checks 含未知检查类型")
        if not checks:
            self.issue("empty_required_checks", "book.yaml:required_checks", "必需检查列表不能为空，不能关闭全部内容检查")
        self.required = [x for x in checks if x in KINDS]
        self.platforms = self.strings(book.get("platforms", ["mac"]), "book.yaml:platforms")
        if "protected_terms" in book:
            self.strings(book["protected_terms"], "book.yaml:protected_terms")
        units = book.get("units")
        if not isinstance(units, list) or not units:
            self.issue("invalid_units", "book.yaml:units", "至少声明一个内容单元")
            units = []
        used_paths = set()
        for unit in units:
            if not self.fields(unit, UNIT_FIELDS, "book.yaml:units", ("id", "title", "path", "depth", "section")):
                continue
            uid = unit.get("id")
            if not isinstance(uid, str) or not SLUG.fullmatch(uid):
                self.issue("invalid_id", "book.yaml:units", "单元 ID 必须是稳定 slug")
                continue
            if uid in self.units:
                self.issue("duplicate_id", "book.yaml:units", "重复单元 ID：" + uid)
                continue
            self.units[uid] = unit
            depth = unit.get("depth")
            if isinstance(depth, bool) or depth not in (0, 1, 2):
                self.issue("invalid_depth", "book.yaml:" + uid, "depth 必须是 0、1 或 2")
            if not isinstance(unit.get("section"), str) or unit.get("section") not in {"popular", "watershed", "deep", "appendix"}:
                self.issue("invalid_section", "book.yaml:" + uid, "未知段落归属")
            if unit.get("section") == "popular" and depth != 0:
                self.issue("popular_depth", "book.yaml:" + uid, "普及段必须从零基础起点解释")
            for field in ("prerequisites", "features", "facts"):
                self.strings(unit.get(field, []), "book.yaml:{}:{}".format(uid, field))
            if "required_checks" in unit:
                required = self.strings(unit["required_checks"], "book.yaml:{}:required_checks".format(uid))
                if not required:
                    self.issue("empty_required_checks", "book.yaml:" + uid, "单元必需检查列表不能为空")
                if set(required) - KINDS:
                    self.issue("invalid_check_kind", "book.yaml:" + uid, "单元 required_checks 含未知检查类型")
                self.unit_required[uid] = [kind for kind in required if kind in KINDS]
            else:
                self.unit_required[uid] = self.required
            derived = unit.get("derived_from")
            if derived is not None:
                self.fields(derived, {"id", "version"}, "book.yaml:" + uid, ("id", "version"))
            p = self.path(unit.get("path"), True)
            if p and p.suffix.lower() not in {".md", ".markdown"}:
                self.issue("invalid_source_format", unit.get("path"), "正文必须是 Markdown 文件")
            if p:
                key = str(p.resolve())
                if key in used_paths:
                    self.issue("duplicate_unit_path", unit["path"], "多个单元不能共用同一正文文件")
                used_paths.add(key)
                try:
                    self.texts[unit["path"]] = p.read_text(encoding="utf-8")
                except (OSError, UnicodeError) as exc:
                    self.issue("unreadable_source", unit["path"], str(exc))
        if self.scope_requested is None:
            self.scope = set(self.units)
        else:
            supplied = [self.scope_requested] if isinstance(self.scope_requested, str) else list(self.scope_requested) if isinstance(self.scope_requested, (list, tuple, set)) else [None]
            self.scope = set(x for x in supplied if isinstance(x, str))
            if self.scope - self.units.keys() or len(self.scope) != len(supplied):
                self.issue("invalid_scope", "book.yaml", "发行范围必须是已声明且不重复的单元 ID")
            if self.publication and not self.scope:
                self.issue("empty_publication_scope", "book.yaml", "公开检查范围不能为空")
        order = {uid: i for i, uid in enumerate(self.units)}
        for uid, unit in self.units.items():
            prereqs = unit.get("prerequisites", [])
            if not isinstance(prereqs, list):
                continue
            for dep in prereqs:
                if not isinstance(dep, str):
                    continue
                if dep not in self.units:
                    self.issue("missing_prerequisite", unit.get("path", uid), "前置单元未登记：" + dep)
                elif order[dep] >= order[uid]:
                    self.issue("prerequisite_order", unit.get("path", uid), "前置须先完成（禁止循环）：" + dep)
            if unit.get("depth") == 2 and book.get("type") == "book" and not prereqs:
                self.issue("missing_prerequisite", unit.get("path", uid), "专业单元须列出前置知识所在单元")
        watershed = book.get("watershed")
        watersheds = [u for u in self.units if self.units[u].get("section") == "watershed"]
        deep = [u for u in self.units if self.units[u].get("section") == "deep" or self.units[u].get("depth") == 2]
        if watersheds and (len(watersheds) != 1 or watershed != watersheds[0]):
            self.issue("watershed_mismatch", "book.yaml", "分水岭声明须对应唯一 watershed 单元")
        if watershed is not None and (not isinstance(watershed, str) or watershed not in self.units):
            self.issue("missing_watershed", "book.yaml", "声明的分水岭不存在")
            watershed = None
        if book.get("type") == "book" and deep:
            if watershed not in order or watershed not in watersheds:
                self.issue("missing_watershed", "book.yaml", "系统书深入段前必须有明确分水岭")
            elif any(order[u] <= order[watershed] for u in deep):
                self.issue("watershed_order", "book.yaml", "专业或深入操作应在分水岭之后")
        self.outputs(used_paths)

    def outputs(self, source_paths):
        outputs = self.book.get("outputs", {})
        if not self.fields(outputs, {"combined", "readme", "pdf", "translations"}, "book.yaml:outputs"):
            return
        paths = set()
        for key in ("combined", "readme"):
            value = outputs.get(key)
            if value is None or value is False:
                continue
            p = self.path(value)
            if p:
                resolved = str(p.resolve())
                parts = p.resolve().relative_to(self.root).parts
                if parts[0] in {"tools", "checks", ".github", ".studio"} or parts[-1] in {"book.yaml", "facts.yaml", "translations.yaml", "translation-overrides.yaml", "AGENTS.md", "CLAUDE.md"}:
                    self.issue("output_collision", value, "生成物不能覆盖配置、审校或工具文件")
                if resolved in source_paths or resolved in paths:
                    self.issue("output_collision", value, "输出不能覆盖正文或另一输出")
                paths.add(resolved)
        pdf = outputs.get("pdf")
        if pdf is not None and self.fields(pdf, {"enabled", "font", "paper"}, "book.yaml:outputs:pdf"):
            if not isinstance(pdf.get("enabled", False), bool):
                self.issue("invalid_type", "book.yaml:outputs:pdf", "enabled 必须是布尔值")
        translations = outputs.get("translations", {})
        if not isinstance(translations, dict):
            self.issue("invalid_type", "book.yaml:translations", "translations 必须是语言映射")
        else:
            for language, config in translations.items():
                if self.fields(config, {"enabled", "directory"}, "book.yaml:translations:" + str(language)):
                    if not isinstance(config.get("enabled", False), bool):
                        self.issue("invalid_type", "book.yaml:translations", "enabled 必须是布尔值")
                    if config.get("directory"):
                        p = self.path(config["directory"])
                        if p and any(Path(s) == p.resolve() or p.resolve() in Path(s).parents for s in source_paths):
                            self.issue("output_collision", config["directory"], "译文目录不能覆盖主语言正文")

    def privacy(self):
        """Inspect only known private locations and public prose/configuration text."""
        for parent, directories, files in os.walk(self.root, followlinks=False):
            parent_path = Path(parent)
            parts = parent_path.relative_to(self.root).parts
            if parts[:2] == ("tools", "tests"):
                directories[:] = []
                continue
            directories[:] = [d for d in directories if d not in SKIP_DIRS]
            if not parts:
                for name in ("private", "reviews", ".ssh"):
                    if name in directories or name in files:
                        self.issue("private_material", name, "私有资料不能放在公开书仓；只报告路径，保留原文件")
                        if name in directories:
                            directories.remove(name)
            for name in files:
                relative = (parent_path / name).relative_to(self.root).as_posix()
                example_env = name in {".env.example", ".env.sample", ".env.template"}
                private_env = (name == ".env" or name.startswith(".env.")) and not example_env
                private_name = name in {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"} or Path(name).suffix.lower() in {".p12", ".pfx"}
                if private_env or private_name or relative == ".aws/credentials":
                    self.issue("private_material", relative, "明确的本机凭据或私钥文件不能放在公开书仓；未输出内容")
                    continue
                if parent_path == self.root and name in {"private", "reviews"}:
                    continue
                if Path(name).suffix.lower() not in {".md", ".markdown", ".yaml", ".yml", ".pem", ".key"} and not example_env:
                    continue
                path = self.path(relative, True)
                if path is None:
                    continue
                try:
                    body = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    continue
                if TOKEN.search(body):
                    self.issue("exposed_credential", relative, "公开文本中检测到明显的凭据格式；请移除并按实际泄露情况处理，未输出值")
                if PRIVATE_KEY.search(body):
                    self.issue("private_key_content", relative, "检测到私钥内容标记；公开书仓不得携带私钥，未输出值")

    def filesystem(self):
        for parent, directories, files in os.walk(self.root, followlinks=False):
            directories[:] = [d for d in directories if d not in SKIP_DIRS and not (Path(parent) == self.root and d in {"private", "reviews", ".ssh"})]
            for name in directories + files:
                p = Path(parent) / name
                relative = p.relative_to(self.root).as_posix()
                if p.is_symlink():
                    self.path(relative)
                if name.endswith(".icloud"):
                    self.issue("icloud_placeholder", relative, "文件未完整下载；保留现场并完成下载")
                elif re.search(r" \d+\.(?:md|ya?ml|json)$", name, re.I):
                    self.issue("icloud_conflict", relative, "疑似 iCloud 冲突副本；需人工确认，不自动删除")
            for name in files:
                if name.lower().endswith((".md", ".markdown")):
                    p = Path(parent) / name
                    relative = p.relative_to(self.root).as_posix()
                    if relative not in self.texts and self.path(relative, True):
                        try:
                            self.texts[relative] = p.read_text(encoding="utf-8")
                        except (OSError, UnicodeError) as exc:
                            self.issue("unreadable_source", relative, str(exc))

    def links(self):
        for relative, content in self.texts.items():
            body = re.sub(r"<!--.*?-->", "", _without_code(content), flags=re.S)
            destinations = [m.group(1) for m in LINK.finditer(body)] + [m.group(1) for m in REFERENCE.finditer(body)]
            for target in destinations:
                target = target.strip("<>")
                target = re.sub(r"\\([() ])", r"\1", target)
                try:
                    parsed = urlsplit(target)
                except ValueError:
                    self.issue("invalid_link", relative, "无法解析链接：" + target)
                    continue
                if parsed.scheme or parsed.netloc:
                    if parsed.scheme == "file":
                        self.issue("private_link", relative, "公开正文不能链接本机 file:// 文件")
                    continue
                raw = unquote(parsed.path)
                raw_path = (Path(relative).parent / raw).as_posix() if raw else relative
                p = self.path(raw_path)
                if p is None:
                    continue
                if not p.exists():
                    self.issue("broken_link", relative, "链接目标不存在：" + target)
                    continue
                fragment = unquote(parsed.fragment)
                if fragment and p.is_file() and p.suffix.lower() in {".md", ".markdown", ".html"}:
                    normalized = p.resolve().relative_to(self.root).as_posix()
                    try:
                        text = self.texts.get(normalized)
                        if text is None:
                            text = p.read_text(encoding="utf-8")
                        if fragment not in _anchors(text):
                            self.issue("broken_fragment", relative, "锚点不存在：" + target)
                    except (OSError, UnicodeError) as exc:
                        self.issue("unreadable_link", relative, str(exc))

    def diagrams(self):
        registry = self.book.get("diagrams", [])
        if not isinstance(registry, list):
            self.issue("invalid_type", "book.yaml:diagrams", "图示登记必须是列表")
            return
        declared, actual = {}, {}
        for diagram in registry:
            if not self.fields(diagram, {"id", "unit", "type"}, "book.yaml:diagrams", ("id", "unit", "type")):
                continue
            did = diagram.get("id")
            if not isinstance(did, str) or not did:
                self.issue("invalid_id", "book.yaml:diagrams", "图 ID 必须是字符串")
                continue
            if did in declared:
                self.issue("duplicate_diagram", "book.yaml", "重复图 ID：" + did)
            declared[did] = diagram
            if not isinstance(diagram.get("unit"), str) or diagram.get("unit") not in self.units:
                self.issue("diagram_unit", "book.yaml", "图示所属单元不存在：" + did)
        for uid, unit in self.units.items():
            relative = unit.get("path")
            text = self.texts.get(relative, "")
            for m in DIAGRAM.finditer(text):
                did = m.group(1)
                if did in actual:
                    self.issue("duplicate_diagram", relative, "正文重复图 ID：" + did)
                actual[did] = uid
                if did not in declared:
                    self.issue("unregistered_diagram", relative, "图示未登记：" + did)
                elif declared[did].get("unit") != uid:
                    self.issue("diagram_unit", relative, "图示登记的所属单元不一致：" + did)
            for m in re.finditer(r"(?:```|~~~)mermaid\s*\n\s*mindmap\b", text):
                prefix = text[:m.start()]
                if not re.search(r"<!--\s*diagram:\s*[^>]+-->\s*$", prefix):
                    self.issue("unregistered_mindmap", relative, "mindmap 前缺少 diagram ID 注释")
        for did in declared.keys() - actual.keys():
            self.issue("missing_diagram", "book.yaml", "登记图示未在正文找到：" + did)

    def fact_records(self):
        if not (self.root / "facts.yaml").exists():
            if any(u.get("facts") for u in self.units.values()):
                self.issue("missing_facts", "facts.yaml", "单元引用了事实，但事实登记不存在")
            data = []
        else:
            data = self.read_yaml("facts.yaml", [])
        if not isinstance(data, list):
            self.issue("invalid_type", "facts.yaml", "事实登记必须是列表")
            data = []
        for fact in data:
            if not self.fields(fact, FACT_FIELDS, "facts.yaml", ("id", "claim", "scope", "sources", "checked_on", "category", "status")):
                continue
            fid = fact.get("id")
            if not isinstance(fid, str) or not SLUG.fullmatch(fid):
                self.issue("invalid_id", "facts.yaml", "事实 ID 必须是 slug")
                continue
            if fid in self.facts:
                self.issue("duplicate_fact", "facts.yaml", "重复事实 ID：" + fid)
            self.facts[fid] = fact
            if not isinstance(fact.get("claim"), str) or not fact["claim"]:
                self.issue("invalid_type", "facts.yaml:" + fid, "claim 必须是非空字符串")
            if not isinstance(fact.get("scope"), dict):
                self.issue("invalid_type", "facts.yaml:" + fid, "scope 必须声明适用条件")
            if not isinstance(fact.get("category"), str) or fact.get("category") not in CATEGORIES:
                self.issue("invalid_category", "facts.yaml:" + fid, "未知事实类别")
            if not isinstance(fact.get("status"), str) or fact.get("status") not in {"confirmed", "unknown", "changed", "false"}:
                self.issue("invalid_fact_status", "facts.yaml:" + fid, "未知事实状态")
            if not isinstance(fact.get("critical", True), bool):
                self.issue("invalid_type", "facts.yaml:" + fid, "critical 必须是布尔值")
            checked = self.check_date(fact.get("checked_on"), "facts.yaml:" + fid)
            sources = fact.get("sources")
            if not isinstance(sources, list):
                self.issue("invalid_type", "facts.yaml:" + fid, "sources 必须是列表")
                sources = []
            for source in sources:
                if self.fields(source, {"url", "checked_on"}, "facts.yaml:" + fid, ("url", "checked_on")):
                    if not isinstance(source.get("url"), str) or not re.match(r"https?://[^/]+", source.get("url", "")):
                        self.issue("invalid_source_url", "facts.yaml:" + fid, "来源必须是完整 HTTP(S) 页面地址")
                    self.check_date(source.get("checked_on"), "facts.yaml:" + fid)
            default_ttl = None if fact.get("category") == "stable" else (90 if fact.get("category") in ("price", "quota", "account") else 180)
            ttl = fact.get("ttl_days", default_ttl)
            if ttl is not None and (isinstance(ttl, bool) or not isinstance(ttl, int) or ttl <= 0):
                self.issue("invalid_ttl", "facts.yaml:" + fid, "ttl_days 须为正整数；稳定概念可为 null")
                ttl = None
            users = [u for u in self.units if isinstance(self.units[u].get("facts", []), list) and fid in self.units[u].get("facts", [])]
            selected = bool(self.scope.intersection(users))
            critical = fact.get("critical", True) and selected
            issue_unit = next(iter(self.scope.intersection(users)), users[0] if users else "")
            if fact.get("status") != "confirmed" or not sources:
                self.quality_issue("fact_unverified", "facts.yaml:" + fid, "事实未知、已变更或无有效来源，需复核", issue_unit, critical)
            if checked and ttl is not None and self.today >= checked + timedelta(days=ttl):
                self.quality_issue("fact_expired", "facts.yaml:" + fid, "事实到期：{}；原核验：{}".format(checked + timedelta(days=ttl), checked), issue_unit, critical)
        for uid, unit in self.units.items():
            refs = unit.get("facts", [])
            if isinstance(refs, list):
                for fid in refs:
                    if isinstance(fid, str) and fid not in self.facts:
                        self.issue("missing_fact", unit.get("path", uid), "未登记事实：" + fid)

    def old_yaml(self, commit, relative):
        key = (commit, relative)
        if key not in self.old_cache:
            try:
                self.old_cache[key] = yaml.safe_load(run_git(self.root, "show", commit + ":" + relative))
            except (StudioError, yaml.YAMLError):
                self.old_cache[key] = None
        return self.old_cache[key]

    def same_file(self, commit, relative):
        p = self.path(relative, True)
        if p is None:
            return False
        try:
            if p.suffix.lower() in {".md", ".markdown"}:
                old = run_git(self.root, "show", commit + ":" + relative)
                return stripped_generated(old) == stripped_generated(p.read_text(encoding="utf-8"))
            return run_git(self.root, "rev-parse", commit + ":" + relative) == run_git(self.root, "hash-object", "--", relative)
        except (StudioError, OSError, UnicodeError):
            return False

    def referenced_resources(self, relative):
        text = self.texts.get(relative, "")
        body = re.sub(r"<!--.*?-->", "", _without_code(text), flags=re.S)
        destinations = [m.group(1) for m in LINK.finditer(body)] + [m.group(1) for m in REFERENCE.finditer(body)]
        destinations += [m.group(1) for m in re.finditer(r"<img\b[^>]*\bsrc=['\"]([^'\"]+)['\"]", body, re.I)]
        resources = set()
        for destination in destinations:
            try:
                parsed = urlsplit(re.sub(r"\\([() ])", r"\1", destination.strip("<>")))
            except ValueError:
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = self.path((Path(relative).parent / unquote(parsed.path)).as_posix())
            if target is not None and target.is_file() and target.suffix.lower() not in {".md", ".markdown"}:
                resources.add(target.resolve().relative_to(self.root).as_posix())
        return sorted(resources)

    def context_current(self, record):
        commit, uid = record["source_commit"], record["unit"]
        paths = record.get("paths", [])
        if self.units[uid].get("path") not in paths:
            return False, "检查路径未包含该单元正文"
        for relative in paths:
            if relative.startswith("checks/"):
                return False, "核验不能把自身检查摘要作为受审输入"
            if not self.same_file(commit, relative):
                return False, "受审文件已变化或基线不存在：" + relative
        for resource in self.referenced_resources(self.units[uid]["path"]):
            if not self.same_file(commit, resource):
                return False, "正文引用的图片或练习附件已变化：" + resource
        old = self.old_yaml(commit, "book.yaml")
        if not isinstance(old, dict):
            return False, "受审提交中缺少 book.yaml，无法确认适用范围"
        old_units = {u.get("id"): u for u in (old.get("units", []) if isinstance(old.get("units"), list) else []) if isinstance(u, dict) and isinstance(u.get("id"), str)}
        if old_units.get(uid) != self.units[uid]:
            return False, "单元前置、事实引用或配置已变化"
        for field in ("type", "product", "language", "watershed", "audience", "baseline", "platforms", "required_checks", "toolkit"):
            if old.get(field) != self.book.get(field):
                return False, "作品适用条件或规则已变化：" + field
        def related_diagrams(book):
            values = book.get("diagrams") or []
            if not isinstance(values, list):
                return None
            return sorted([d for d in values if isinstance(d, dict) and d.get("unit") == uid], key=lambda d: str(d.get("id", "")))
        if related_diagrams(old) != related_diagrams(self.book):
            return False, "本单元的图示声明已变化"
        refs = self.units[uid].get("facts", [])
        if refs:
            old_facts = self.old_yaml(commit, "facts.yaml")
            if not isinstance(old_facts, list):
                return False, "受审事实基线不存在"
            old_by_id = {f.get("id"): f for f in old_facts if isinstance(f, dict) and isinstance(f.get("id"), str)}
            if any(old_by_id.get(fid) != self.facts.get(fid) for fid in refs):
                return False, "引用事实已变化"
        for dep in self.units[uid].get("prerequisites", []):
            if dep in self.units and (old_units.get(dep) != self.units[dep] or not self.same_file(commit, self.units[dep]["path"])):
                return False, "前置单元发生变化：" + dep
        try:
            changed = run_git(self.root, "diff", "--name-only", commit, "--", "tools/standards", "术语翻译表.md", "写作规范.md", "写作规范-本书补充.md")
            if changed:
                return False, "有关写作规范或术语发生变化"
        except StudioError as exc:
            return False, str(exc)
        return True, ""

    def review_records(self):
        directory = self.root / "checks"
        if directory.exists() and self.path("checks"):
            for p in sorted(directory.glob("*.y*ml")):
                relative = p.relative_to(self.root).as_posix()
                data = self.read_yaml(relative, [])
                records = data if isinstance(data, list) else [data]
                for record in records:
                    if not self.fields(record, RECORD_FIELDS, relative, ("unit", "source_commit", "paths", "kind", "result", "checked_on")):
                        continue
                    uid, kind = record.get("unit"), record.get("kind")
                    if not isinstance(uid, str) or uid not in self.units:
                        self.issue("unknown_review_unit", relative, "审校单元未登记")
                        continue
                    if not isinstance(kind, str) or kind not in KINDS or not isinstance(record.get("result"), str) or record.get("result") not in {"pass", "fail", "unknown", "not_applicable"}:
                        self.issue("invalid_review_status", relative, "未知检查类型或结果")
                        continue
                    paths = self.strings(record.get("paths"), relative + ":paths")
                    for path in paths:
                        self.path(path, True)
                    checked = self.check_date(record.get("checked_on"), relative)
                    current, problem = False, "受审提交不可解析"
                    commit = record.get("source_commit")
                    if isinstance(commit, str) and SHA.fullmatch(commit) and paths:
                        try:
                            if git_commit(self.root, commit) == commit:
                                run_git(self.root, "merge-base", "--is-ancestor", commit, "HEAD")
                                current, problem = self.context_current(record)
                        except StudioError as exc:
                            problem = str(exc)
                    for field in ("limitations", "reason"):
                        if field in record and not isinstance(record[field], str):
                            self.issue("invalid_type", relative, field + " 必须是文字")
                        if isinstance(record.get(field), str) and re.search(r"(?:/Users/|/home/|(?:^|\s)private/|(?:^|\s)reviews/)", record[field]):
                            self.issue("private_review_data", relative, "公开摘要不得包含私有报告或个人目录路径")
                    self.records.append({"record": record, "path": relative, "date": checked or date.min, "current": current, "problem": problem})
        for uid in self.units:
            self.quality[uid] = {}
            for kind in KINDS:
                group = [r for r in self.records if r["record"]["unit"] == uid and r["record"]["kind"] == kind]
                required = kind in self.unit_required.get(uid, getattr(self, "required", []))
                if not group:
                    self.quality[uid][kind] = "unknown"
                    if required:
                        self.quality_issue("missing_review", self.units[uid].get("path", uid), "{} 缺少 {} 检查；历史发布不是核验依据".format(uid, kind), uid)
                    continue
                current = [r for r in group if r["current"]]
                candidates = current or group
                latest = max(r["date"] for r in candidates)
                candidates = [r for r in candidates if r["date"] == latest]
                # If equally recent declarations disagree, a failure wins until explicitly resolved.
                selected = sorted(candidates, key=lambda r: r["record"]["result"] == "pass")[0]
                r = selected["record"]
                state, reason = r["result"], ""
                if not selected["current"]:
                    state, reason = "stale", selected["problem"]
                elif state == "not_applicable" and (required or not r.get("reason")):
                    state, reason = "unknown", "必需检查不能以不适用跳过；其他不适用须说明理由"
                elif state in {"fail", "unknown"}:
                    reason = "检查结果为 " + state
                elif state == "pass" and kind == "editorial":
                    engine, author = r.get("engine"), r.get("author_engine")
                    if engine == "human":
                        if not r.get("reason"):
                            state, reason = "unknown", "人工替代交叉审校需说明接受理由"
                    elif engine not in ("claude", "codex") or author not in ("claude", "codex", "human") or engine == author:
                        state, reason = "unknown", "编辑审校须记录不同的起草与审校引擎"
                elif state == "pass" and kind == "trial" and r.get("engine") != "human":
                    state, reason = "unknown", "真实试读需明确为 human；AI 模拟不能算目标读者试读"
                elif state == "pass" and kind == "operations":
                    platforms = r.get("platforms", [])
                    if not isinstance(platforms, list) or not all(isinstance(p, str) for p in platforms) or not set(getattr(self, "platforms", ["mac"])).issubset(platforms):
                        state, reason = "unknown", "实测未覆盖全部承诺平台"
                self.quality[uid][kind] = state
                if state not in {"pass", "not_applicable"}:
                    self.quality_issue("review_" + state, selected["path"], "{} {}：{}".format(uid, kind, reason), uid, required)

    def result(self):
        return {"ok": not any(i["level"] == "error" for i in self.issues), "issues": self.issues,
                "summary": {"book": self.book.get("id"), "units": len(self.units), "facts": len(self.facts),
                            "publication": self.publication, "scope": sorted(self.scope), "quality": self.quality,
                            "errors": sum(i["level"] == "error" for i in self.issues),
                            "warnings": sum(i["level"] == "warning" for i in self.issues)}}


def check_book(book_dir, publication=False, scope=None, today=None, freshness=True, source_only=False):
    """Check local book files; never fetch, write source files, or infer real-world verification."""
    checker = _Checker(book_dir, publication, scope, today)
    checker.privacy()
    checker.configuration()
    checker.filesystem()
    if source_only:
        outputs = checker.book.get("outputs") or {}
        if isinstance(outputs, dict):
            combined = outputs.get("combined")
            translations = outputs.get("translations") or {}
            generated_roots = []
            if isinstance(translations, dict):
                for language, config in translations.items():
                    if isinstance(config, dict) and config.get("enabled") and isinstance(config.get("directory", language), str):
                        generated_roots.append(config.get("directory", language).rstrip("/") + "/")
            checker.texts = {path: re.sub(r"<!-- studio:(nav|toc|release) -->.*?<!-- /studio:\1 -->", "", text, flags=re.S)
                             for path, text in checker.texts.items()
                             if path != combined and not any(path.startswith(prefix) for prefix in generated_roots)}
        if publication:
            checker.issue("invalid_check_mode", "book.yaml", "source_only 用于构建前检查，不能作为公开质量检查")
    checker.links()
    checker.diagrams()
    checker.fact_records()
    # Invalid schemas cannot safely be interpreted as valid review dependencies.
    if not any(i["level"] == "error" for i in checker.issues):
        checker.review_records()
    if freshness and not source_only and not any(i["level"] == "error" for i in checker.issues):
        try:
            from .builder import build_book
        except ImportError:
            checker.issue("freshness_unavailable", "book.yaml", "构建器尚不可用，未验证生成物新鲜度", "warning")
        else:
            try:
                result = build_book(checker.root, check_only=True)
                for item in result.get("issues", []):
                    checker.issue(item.get("code", "build_freshness"), item.get("path", "book.yaml"), item.get("message", str(item)), item.get("level", "error"))
                if not result.get("ok", False) and not result.get("issues"):
                    checker.issue("stale_generated", "book.yaml", "生成物与源稿不一致：" + str(result.get("changed", result.get("message", "运行 studio build 更新"))))
            except StudioError as exc:
                checker.issue("build_freshness", "book.yaml", str(exc))
    result = checker.result()
    result["summary"]["source_only"] = bool(source_only)
    return _redacted(result)
