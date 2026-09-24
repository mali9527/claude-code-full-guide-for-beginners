"""Offline product-change impact proposals, with one private tasks.md per work.

Tags locate review candidates; no match never means a product change is harmless.
This module does not research products, modify manuscripts, or publish anything.
"""
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re
import yaml

from .common import StudioError, atomic_write, load_yaml, safe_path, git_commit

ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _identifier(value, field):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise StudioError("{} 必须是稳定 slug".format(field))
    return value


def _strings(value, field):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise StudioError("{} 必须是字符串列表".format(field))
    return sorted(set(value))


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n"


def _digest(value):
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _change(value):
    fields = {"id", "product", "features", "facts", "source_url", "discovered_on", "summary"}
    if not isinstance(value, dict) or set(value) - fields:
        raise StudioError("变化条目必须是映射，且只含约定字段")
    output = {"id": _identifier(value.get("id"), "change.id"),
              "product": _identifier(value.get("product"), "change.product")}
    for field in ("features", "facts"):
        output[field] = _strings(value.get(field, []), "change." + field)
    url = value.get("source_url")
    try:
        parsed = urlsplit(url) if isinstance(url, str) else None
    except ValueError:
        parsed = None
    if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc or re.search(r"[\x00-\x20]", url):
        raise StudioError("变化来源需要完整 HTTP(S) URL；本工具不会联网")
    output["source_url"] = url
    discovered = value.get("discovered_on")
    try:
        if isinstance(discovered, datetime):
            discovered = discovered.date()
        if not isinstance(discovered, date):
            discovered = date.fromisoformat(discovered)
        output["discovered_on"] = discovered.isoformat()
    except (TypeError, ValueError):
        raise StudioError("discovered_on 必须是 YYYY-MM-DD")
    summary = value.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise StudioError("变化必须有可读 summary，不能只写标签")
    output["summary"] = summary.strip()
    return output


def _read_optional(path, default):
    return load_yaml(path) if path.exists() else default


def _social_posts(workspace, work_id):
    """Accept per-post YAML, index.yaml entries, or Markdown YAML front matter."""
    base = safe_path(workspace, "private/{}/social-posts".format(work_id))
    if not base.exists():
        return []
    if not base.is_dir():
        raise StudioError("社交短文路径必须是目录：{}".format(base))
    records, associated = [], set()
    for source in sorted(base.rglob("*")):
        safe_path(base, source.relative_to(base).as_posix())
        if not source.is_file() or source.suffix.lower() not in {".yaml", ".yml", ".md"}:
            continue
        relative = source.relative_to(base).as_posix()
        if source.suffix.lower() == ".md":
            try:
                text = source.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise StudioError("{}: {}".format(source, exc))
            match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.S)
            if not match:
                records.append({"path": relative, "_missing": True})
                continue
            try:
                value = yaml.safe_load(match.group(1))
            except yaml.YAMLError as exc:
                raise StudioError("{}: {}".format(source, exc))
        else:
            value = load_yaml(source)
        if isinstance(value, dict) and "entries" in value:
            data = value["entries"]
        else:
            data = value if isinstance(value, list) else [value]
        if not isinstance(data, list):
            raise StudioError("{}: 社交短文元信息需要记录或 entries 列表".format(source))
        for item in data:
            if not isinstance(item, dict):
                raise StudioError("{}: 无效社交短文记录".format(source))
            record = dict(item)
            target = record.get("path")
            if target is None:
                sibling = source.with_suffix(".md")
                target = sibling.relative_to(base).as_posix() if sibling.exists() else relative
            safe_path(base, target)
            record["path"] = target
            for key in ("id", "status", "published_url", "product"):
                if record.get(key) is not None and not isinstance(record[key], str):
                    raise StudioError("social-post.{} 必须是文字".format(key))
            for field in ("units", "facts", "features"):
                record[field] = _strings(record.get(field, []), "social-post." + field)
            associated.add(target)
            records.append(record)
    return [r for r in records if not r.get("_missing") or r["path"] not in associated]


def _work(workspace, registration):
    if not isinstance(registration, dict):
        raise StudioError("workspace.works 必须是作品登记列表")
    wid = _identifier(registration.get("id"), "work.id")
    root = safe_path(workspace, registration.get("path"))
    book = load_yaml(safe_path(root, "book.yaml"))
    if not isinstance(book, dict) or book.get("id") != wid:
        raise StudioError("{}: 作品身份与 workspace 不一致".format(root))
    _identifier(book.get("product"), "book.product")
    units = book.get("units")
    if not isinstance(units, list) or not units:
        raise StudioError("{}: 缺少单元清单".format(root))
    indexed = {}
    for value in units:
        if not isinstance(value, dict):
            raise StudioError("book.units 必须是单元映射列表")
        unit = dict(value)
        uid = _identifier(unit.get("id"), "unit.id")
        if uid in indexed:
            raise StudioError("{}: 重复单元 {}".format(wid, uid))
        if not isinstance(unit.get("title", uid), str):
            raise StudioError("unit.title 必须是文字")
        safe_path(root, unit.get("path"))
        for field in ("features", "facts", "prerequisites"):
            unit[field] = _strings(unit.get(field, []), "unit." + field)
        indexed[uid] = unit
    facts = _read_optional(safe_path(root, "facts.yaml"), [])
    if not isinstance(facts, list):
        raise StudioError("facts.yaml 必须是列表")
    try:
        source_commit = git_commit(root)
    except StudioError:
        source_commit = None
    return {"id": wid, "path": registration["path"], "root": root,
            "book": book, "units": indexed, "facts": facts,
            "source_commit": source_commit, "social": _social_posts(workspace, wid)}


def _analyze(work, change):
    book, units = work["book"], work["units"]
    primary = book.get("product") == change["product"]
    external_facts = {f["id"] for f in work["facts"]
                      if isinstance(f, dict) and isinstance(f.get("id"), str)
                      and isinstance(f.get("scope"), dict) and f["scope"].get("product") == change["product"]}
    related_units = {uid for uid, u in units.items() if external_facts.intersection(u["facts"])}
    relevant_posts = [p for p in work["social"] if p.get("product") == change["product"]]
    if not primary and not related_units and not relevant_posts:
        return None
    classifications, reasons = {}, {}
    for uid, unit in units.items():
        if not primary and uid not in related_units:
            continue
        facts = set(unit["facts"]).intersection(change["facts"])
        if not primary:
            facts.intersection_update(external_facts)
        features = set(unit["features"]).intersection(change["features"]) if primary else set()
        if facts or features:
            classifications[uid] = "certain"
            reasons[uid] = ["明确引用变化事实：" + ", ".join(sorted(facts))] if facts else []
            if features:
                reasons[uid].append("功能标签直接命中：" + ", ".join(sorted(features)))
        else:
            classifications[uid] = "unknown"
            reasons[uid] = ["标签或事实未直接命中；需要人工判断，不能认定无影响"]
    # Propagate only from explicit or already propagated matches, never from an unknown.
    changed = True
    while changed:
        changed = False
        impacted = {u for u, kind in classifications.items() if kind in {"certain", "possible"}}
        for uid, unit in units.items():
            deps = impacted.intersection(unit["prerequisites"])
            if deps and classifications.get(uid) not in {"certain", "possible"}:
                classifications[uid] = "possible"
                reasons[uid] = ["依赖可能受影响的前置：" + ", ".join(sorted(deps))]
                changed = True
    groups = {"certain": [], "possible": [], "unknown": []}
    for uid in units:
        if uid in classifications:
            unit = units[uid]
            groups[classifications[uid]].append({"unit": uid, "title": unit.get("title", uid),
                                                  "path": unit["path"], "reasons": reasons[uid]})
    derivatives = []
    translations = ((book.get("outputs") or {}).get("translations") or {})
    if not isinstance(translations, dict):
        raise StudioError("outputs.translations 必须是语言配置映射")
    for language, config in translations.items():
        if not isinstance(config, dict) or not config.get("enabled"):
            continue
        directory = config.get("directory", language)
        safe_path(work["root"], directory)
        for uid, category in classifications.items():
            path = (Path(directory) / units[uid]["path"]).as_posix()
            safe_path(work["root"], path)
            derivatives.append({"type": "translation", "language": language, "unit": uid, "path": path,
                                "category": "possible" if category != "unknown" else "unknown",
                                "reason": "原单元待核查；译文须核对对应基线，不能直接自动重写"})
    impact_units = {u for u, kind in classifications.items() if kind != "unknown"}
    for post in work["social"]:
        if not primary and post not in relevant_posts and not impact_units.intersection(post.get("units", [])) and not external_facts.intersection(post.get("facts", [])):
            continue
        direct = set(post.get("facts", [])).intersection(change["facts"])
        features = set(post.get("features", [])).intersection(change["features"])
        deps = impact_units.intersection(post.get("units", []))
        if direct or features:
            category, reason = "certain", "短文元信息直接引用变化事实或功能标签"
        elif deps:
            category, reason = "possible", "短文关联受影响单元：" + ", ".join(sorted(deps))
        else:
            category, reason = "unknown", "缺少完整关联或未命中；不能根据历史文件日期推断状态"
        derivatives.append({"type": "social-post", "id": post.get("id"), "path": "private/{}/social-posts/{}".format(work["id"], post["path"]),
                            "category": category, "reason": reason, "status": post.get("status", "unknown"),
                            "published_url": post.get("published_url")})
    task_id = "SUG-" + _digest([work["id"], change["product"], change["id"]])[:12]
    return {"work_id": work["id"], "book_path": work["path"], "source_commit": work["source_commit"],
            "groups": groups, "derivatives": derivatives,
            "task": {"id": task_id, "path": "private/{}/tasks.md".format(work["id"]), "action": "proposed"}}


def _task_text(analysis, change):
    task_id = analysis["task"]["id"]
    lines = ["## {} 核查产品变化 {}".format(task_id, change["id"]), "", "状态：待做", "",
             "- 目标：{}".format(change["summary"].replace("\n", " ")),
             "- 输入：{}；发现于 {}；产品 {}。".format(change["source_url"], change["discovered_on"], change["product"]),
             "- 源稿提交：{}；这是定位信息，不代表已经实测。".format(analysis["source_commit"] or "尚未保存提交"),
             "- 允许改：本建议尚未批准正文写入；先核查影响，再按已授权任务范围修订。",
             "- 分工：待作者或主控安排；建议卡不代表已开始生产。",
             "- 验收：确定影响范围；必要事实、操作、编辑和衍生物检查分别记录。",
             "- 交接：尚未执行研究、改稿或发布。",
             "- 变化记录：[独立修订记录](changes/{}/)。".format(task_id), ""]
    for group, title in (("certain", "确定受影响"), ("possible", "可能受影响"), ("unknown", "尚无法判断")):
        names = [item["unit"] for item in analysis["groups"][group]]
        lines.append("- {}：{}".format(title, ", ".join(names) if names else "无已定位项"))
    if analysis["derivatives"]:
        lines.append("- 衍生物：{} 项需核对，见变化记录；不自动更新。".format(len(analysis["derivatives"])))
    return "\n".join(lines).rstrip() + "\n"


def _apply(workspace, change, analysis):
    task = analysis["task"]
    target = safe_path(workspace, task["path"])
    record_dir = safe_path(workspace, "private/{}/changes/{}".format(analysis["work_id"], task["id"]))
    payload = {"change": change, "work_id": analysis["work_id"], "book_path": analysis["book_path"],
               "groups": analysis["groups"], "derivatives": analysis["derivatives"]}
    # Commit-only bookkeeping changes do not create new impact proposals.
    fingerprint = _digest(payload)
    record_path = safe_path(record_dir, fingerprint + ".json")
    note_path = safe_path(record_dir, fingerprint + ".md")
    if target.exists() and not target.is_file():
        raise StudioError("任务看板不是文件：{}".format(target))
    text = target.read_text(encoding="utf-8") if target.exists() else "# 任务看板\n"
    matches = list(re.finditer(r"^##\s+" + re.escape(task["id"]) + r"(?:\s|$)", text, re.M))
    if len(matches) > 1:
        raise StudioError("{}: 稳定任务 ID 重复；请先合并记录".format(target))
    known = record_dir.exists() and any(record_dir.glob("*.json"))
    if record_path.exists():
        try:
            existing = json.loads(record_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise StudioError("变化记录损坏；保留现场：{}".format(exc))
        if existing.get("payload") != payload:
            raise StudioError("变化记录内容与标识不一致；不覆盖：{}".format(record_path))
        task["action"] = "unchanged" if matches else "task_missing"
        task["record"] = record_path.relative_to(workspace).as_posix()
        if not matches:
            task["notice"] = "已有变化记录，但任务卡已不在看板；请人工确认，不自动重建"
        return
    if not matches:
        text = text.rstrip() + "\n\n" + _task_text(analysis, change)
        atomic_write(target, text)
        task["action"] = "created"
    else:
        task["action"] = "revision_needed" if known else "recorded_existing"
    task["record"] = record_path.relative_to(workspace).as_posix()
    stored = {"task_id": task["id"], "fingerprint": fingerprint, "source_commit": analysis["source_commit"],
              "requires_review": bool(matches), "payload": payload}
    atomic_write(record_path, _json(stored))
    if known:
        task["notice"] = "变化内容或影响范围有新版本；原任务人工内容保持不变，请复核范围"
        atomic_write(note_path, "# {} 的变化修订提示\n\n{}\n\n来源：{}\n\n详情：[本次影响记录]({})\n\n请保留原任务中的人工进度和结论，判断是否需要调整。\n".format(
            task["id"], task["notice"], change["source_url"], record_path.name))
        task["notice_path"] = note_path.relative_to(workspace).as_posix()


def impact_changes(root, changes, apply=False):
    """Analyze explicit product changes; apply only appends private proposed task cards.

    Returns {ok, applied, changes:[{change_id, product, works:[analysis], status}], summary}.
    Each analysis has groups.certain/possible/unknown, derivatives and task metadata.
    """
    workspace = Path(root).resolve()
    config = load_yaml(safe_path(workspace, "workspace.yaml"))
    if not isinstance(config, dict) or not isinstance(config.get("works"), list):
        raise StudioError("workspace.yaml 必须声明 works 列表")
    values = [changes] if isinstance(changes, dict) else changes
    if not isinstance(values, list) or not values:
        raise StudioError("changes 必须包含至少一条变化记录")
    normalized, identities = [], {}
    for value in values:
        change = _change(value)
        identity = (change["product"], change["id"])
        if identity in identities:
            if identities[identity] != change:
                raise StudioError("同一次输入含两个不同的同 ID 变化版本：{}".format(change["id"]))
            continue
        identities[identity] = change
        normalized.append(change)
    works, ids = [], set()
    for registration in config["works"]:
        work = _work(workspace, registration)
        if work["id"] in ids:
            raise StudioError("workspace 出现重复作品 ID：" + work["id"])
        ids.add(work["id"])
        works.append(work)
    output = []
    for change in normalized:
        analyses = [value for value in (_analyze(work, change) for work in works) if value is not None]
        # Preflight private destinations before any write to avoid partial work on unsafe targets.
        for analysis in analyses:
            safe_path(workspace, analysis["task"]["path"])
            safe_path(workspace, "private/{}/changes/{}".format(analysis["work_id"], analysis["task"]["id"]))
        output.append({"change_id": change["id"], "product": change["product"], "works": analyses,
                       "status": "analyzed" if analyses else "unmapped",
                       "note": "确定表示必须检查，不代表已证明正文需要改写" if analyses else "没有关联作品登记；影响尚无法判断"})
    if apply:
        for change, item in zip(normalized, output):
            for analysis in item["works"]:
                _apply(workspace, change, analysis)
    actions = [a["task"]["action"] for item in output for a in item["works"]]
    return {"ok": True, "applied": bool(apply), "changes": output,
            "summary": {"changes": len(output), "work_analyses": len(actions),
                        "created": actions.count("created"), "revision_needed": actions.count("revision_needed"),
                        "unmapped": sum(i["status"] == "unmapped" for i in output)}}
