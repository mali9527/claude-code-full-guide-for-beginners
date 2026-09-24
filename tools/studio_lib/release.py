"""Small, explicit release pipeline; no command in this module runs on import.

Content review is the caller's responsibility. prepare_release refuses a dirty
book, freezes a commit and copies assets. publish/resume consume that plan; they
never rebuild, push a branch, replace an asset, or move an existing tag.

The GhRemote transport uses the signed-in gh identity. API contracts checked:
https://docs.github.com/en/rest/releases/releases
https://docs.github.com/en/rest/releases/assets
https://docs.github.com/en/rest/git/refs
https://cli.github.com/manual/gh_api
Real-network integration is deliberately separate from FakeRemote tests.
"""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from urllib.parse import quote
import yaml

from .common import StudioError, atomic_write, git_commit, run_git, safe_path


_VERSION = re.compile(r"v\d{4}\.\d{2}\.\d+(?:-rc\.\d+)?\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_ASSET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_write(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _json_read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise StudioError("无法读取发布记录 {}：{}".format(path, exc))


def _digest(path):
    h = hashlib.sha256()
    try:
        with Path(path).open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
    except OSError as exc:
        raise StudioError("无法读取附件 {}：{}".format(path, exc))
    return h.hexdigest()


def _repo(value):
    if not isinstance(value, str) or not _REPO.fullmatch(value):
        raise StudioError("仓库必须明确写为 owner/repo：{}".format(value))
    if any(part in (".", "..") for part in value.split("/")):
        raise StudioError("无效仓库身份")
    return value


def _plan_file(path):
    path = Path(path).resolve()
    return path / "plan.json" if path.is_dir() else path


def _validate_plan(plan):
    if not isinstance(plan, dict) or plan.get("format_version") != 1:
        raise StudioError("未知发布清单格式")
    for key in ("work_id", "repository", "tag", "commit", "kind", "source_version",
                "title", "notes", "assets", "promote", "expected_previous", "is_test", "scope"):
        if key not in plan:
            raise StudioError("发布清单缺少字段：" + key)
    _repo(plan["repository"])
    if not isinstance(plan["work_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", plan["work_id"]):
        raise StudioError("发布清单缺少有效作品 ID")
    if not isinstance(plan["commit"], str) or not _SHA.fullmatch(plan["commit"]):
        raise StudioError("发布清单必须记录完整提交 SHA")
    if not isinstance(plan["title"], str) or not isinstance(plan["notes"], str):
        raise StudioError("发布标题与说明必须是文本")
    if not isinstance(plan["source_version"], str) or not _VERSION.fullmatch(plan["source_version"]):
        raise StudioError("无效正文版本")
    if not isinstance(plan["tag"], str):
        raise StudioError("标签必须是文本")
    if plan["kind"] == "pdf":
        pattern = r"pdf-" + re.escape(plan["source_version"]) + r"-\d{2,}\Z"
        if not re.fullmatch(pattern, plan["tag"]):
            raise StudioError("PDF 标签应为 pdf-正文版本-01")
        if plan["promote"]:
            raise StudioError("PDF 导出版不能提升为正文 latest")
    elif plan["kind"] != "milestone" or plan["tag"] != plan["source_version"]:
        raise StudioError("里程碑标签必须等于正文版本")
    if "-rc." in plan["source_version"] and plan["promote"]:
        raise StudioError("预发行不能提升为正式 latest")
    if not isinstance(plan["assets"], list):
        raise StudioError("附件清单必须是列表")
    names = set()
    for asset in plan["assets"]:
        if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
            raise StudioError("附件条目缺少文件名")
        name = asset["name"]
        if not _ASSET.fullmatch(name) or name in names:
            raise StudioError("附件名必须唯一且为安全 ASCII 文件名：" + name)
        names.add(name)
        if asset.get("path") != "assets/" + name:
            raise StudioError("附件必须引用本清单目录中的冻结副本")
        if not re.fullmatch(r"[0-9a-f]{64}", str(asset.get("sha256", ""))):
            raise StudioError("附件缺少 SHA-256：" + name)
        if not isinstance(asset.get("size"), int) or asset["size"] < 0:
            raise StudioError("无效附件大小：" + name)
    if plan["kind"] == "pdf" and not any(a["name"].lower().endswith(".pdf") for a in plan["assets"]):
        raise StudioError("PDF 导出版至少需要一份 PDF 附件")
    if not isinstance(plan["promote"], bool) or not isinstance(plan["is_test"], bool):
        raise StudioError("promote/is_test 必须为布尔值")
    scope = plan["scope"]
    if not isinstance(scope, dict) or set(scope) != {"units", "languages"}:
        raise StudioError("公开范围必须包含 units 和 languages")
    for key in ("units", "languages"):
        if not isinstance(scope[key], list) or any(not isinstance(x, str) or not x for x in scope[key]):
            raise StudioError("公开范围 {} 必须是文本列表".format(key))
        if len(scope[key]) != len(set(scope[key])):
            raise StudioError("公开范围包含重复项：" + key)
    if not scope["languages"]:
        raise StudioError("公开范围至少包含一种语言")
    return plan


def _load_plan(path):
    path = _plan_file(path)
    return path, _validate_plan(_json_read(path))


def _frozen_asset(plan_path, asset):
    path = safe_path(plan_path.parent, asset["path"])
    if not path.is_file() or path.is_symlink():
        raise StudioError("冻结附件缺失或是符号链接：" + asset["name"])
    if path.stat().st_size != asset["size"] or _digest(path) != asset["sha256"]:
        raise StudioError("冻结附件已改变，需重新准备新版本：" + asset["name"])
    return path


def prepare_release(book_dir, records_dir, *, version, source_ref="HEAD", assets=None,
                    title=None, notes="", kind="milestone", source_version=None,
                    promote=False, expected_previous=None, repository=None, scope=None):
    """Freeze a local release in records_dir/version/plan.json (no network).

    assets is a list of paths, or {path: ..., name: ...} entries. Records must be
    outside the public book. A repeated identical preparation returns the same
    plan; an existing different plan is never overwritten.
    """
    if not isinstance(version, str) or not version:
        raise StudioError("必须指定发行版本")
    book_dir = Path(book_dir).resolve()
    if Path(run_git(book_dir, "rev-parse", "--show-toplevel")).resolve() != book_dir:
        raise StudioError("必须指定单书 Git 根目录")
    if run_git(book_dir, "status", "--porcelain", "--untracked-files=all"):
        raise StudioError("书仓有未提交或未跟踪修改；先审阅并保存，再准备发行")
    commit = git_commit(book_dir, source_ref)
    try:
        book = yaml.safe_load(run_git(book_dir, "show", commit + ":book.yaml"))
    except yaml.YAMLError as exc:
        raise StudioError("来源提交中的 book.yaml 无法解析：{}".format(exc))
    if not isinstance(book, dict) or not isinstance(book.get("repository"), dict):
        raise StudioError("book.yaml 缺少 repository 配置")
    configured = _repo(book["repository"].get("name"))
    repository = _repo(repository or configured)
    if repository.lower() != configured.lower():
        raise StudioError("显式目标仓库与 book.yaml 不一致")
    branch = book["repository"].get("default_branch", "main")
    if not isinstance(branch, str) or branch.startswith("-"):
        raise StudioError("无效默认分支")
    run_git(book_dir, "merge-base", "--is-ancestor", commit, "refs/heads/" + branch)
    source_version = source_version or version
    if not isinstance(source_version, str) or not _VERSION.fullmatch(source_version):
        raise StudioError("正文版本必须是 vYYYY.MM.N 或其 rc 版本")
    if kind == "pdf":
        if git_commit(book_dir, "refs/tags/" + source_version) != commit:
            raise StudioError("PDF 来源版本标签与指定提交不一致")
    try:
        existing_tag = git_commit(book_dir, "refs/tags/" + version)
    except StudioError:
        existing_tag = None
    if existing_tag and existing_tag != commit:
        raise StudioError("本地同名标签已指向其他提交")
    entries, originals = [], []
    for item in assets or []:
        src = Path(item["path"] if isinstance(item, dict) else item).resolve()
        name = item.get("name", src.name) if isinstance(item, dict) else src.name
        if not isinstance(name, str) or not _ASSET.fullmatch(name):
            raise StudioError("附件名必须为安全 ASCII 文件名")
        if not src.is_file():
            raise StudioError("附件不存在：{}".format(src))
        entries.append({"name": name, "path": "assets/" + name,
                        "sha256": _digest(src), "size": src.stat().st_size})
        originals.append(src)
    units = book.get("units", [])
    if not isinstance(units, list) or any(not isinstance(u, dict) or not isinstance(u.get("id"), str) for u in units):
        raise StudioError("来源提交的单元清单格式不符")
    known_units = [unit["id"] for unit in units]
    primary_language = book.get("language", "zh-CN")
    scope = deepcopy(scope) if scope is not None else {"units": known_units, "languages": [primary_language]}
    plan = _validate_plan({
        "format_version": 1, "work_id": book.get("id"), "repository": repository,
        "repository_id": book["repository"].get("id"), "tag": version,
        "commit": commit, "kind": kind, "source_version": source_version,
        "title": title if title is not None else version, "notes": notes,
        "assets": entries, "promote": promote, "expected_previous": expected_previous,
        "is_test": book.get("is_test", False), "scope": scope,
    })
    if not set(scope["units"]).issubset(known_units):
        raise StudioError("公开范围包含来源提交中不存在的单元")
    outputs = book.get("outputs", {})
    if not isinstance(outputs, dict) or not isinstance(outputs.get("translations", {}), dict):
        raise StudioError("来源提交的输出/译文配置格式不符")
    translation_config = outputs.get("translations", {})
    known_languages = {primary_language} | {
        name for name, settings in translation_config.items()
        if isinstance(settings, dict) and settings.get("enabled")
    }
    if not set(scope["languages"]).issubset(known_languages):
        raise StudioError("公开范围包含来源提交中未启用的语言")
    records = Path(records_dir).resolve()
    if records == book_dir or book_dir in records.parents:
        raise StudioError("私有发布记录不能保存在公开书仓中")
    destination = safe_path(records, version)
    plan_path = destination / "plan.json"
    if destination.exists():
        old = _json_read(plan_path)
        if {k: v for k, v in old.items() if k != "prepared_at"} != plan:
            raise StudioError("该版本已有不同发布清单；请审阅原计划或使用新版本")
        for asset in old["assets"]:
            _frozen_asset(plan_path, asset)
        return {"ok": True, "plan_path": str(plan_path), "plan": old, "reused": True}
    records.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".release-", dir=str(records)))
    try:
        (staging / "assets").mkdir()
        for entry, original in zip(entries, originals):
            target = staging / entry["path"]
            shutil.copyfile(str(original), str(target))
            if _digest(target) != entry["sha256"]:
                raise StudioError("复制过程中附件改变：" + entry["name"])
        plan["prepared_at"] = _now()
        _json_write(staging / "plan.json", plan)
        os.rename(str(staging), str(destination))
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {"ok": True, "plan_path": str(plan_path), "plan": plan, "reused": False}


class GhRemote:
    """GitHub.com REST transport through gh. No tokens are read or saved here."""

    def __init__(self, repository):
        self.repository = _repo(repository)
        self.base = "repos/" + self.repository

    def _api(self, endpoint, method="GET", payload=None, allow404=False,
             raw=False, accept="application/vnd.github+json", content_type=None):
        cmd = ["gh", "api", "--hostname", "github.com", "--method", method,
               endpoint, "-H", "Accept: " + accept,
               "-H", "X-GitHub-Api-Version: 2026-03-10"]
        data = None
        if payload is not None:
            data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
            cmd += ["--input", "-"]
        if content_type:
            cmd += ["-H", "Content-Type: " + content_type]
        try:
            result = subprocess.run(cmd, input=data, capture_output=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise StudioError("gh 请求未完成；写入结果可能不明，请 audit 后恢复：{}".format(exc))
        if result.returncode:
            error = result.stderr.decode("utf-8", "replace").strip()
            if allow404 and re.search(r"HTTP 404\b", error):
                return None
            raise StudioError("GitHub {} {} 失败：{}".format(method, endpoint, error))
        if raw:
            return result.stdout
        if not result.stdout.strip():
            return None
        try:
            return json.loads(result.stdout)
        except ValueError:
            raise StudioError("GitHub 返回无法解析的响应，请核对远端后恢复")

    def _list(self, endpoint):
        results = []
        for page in range(1, 10001):
            sep = "&" if "?" in endpoint else "?"
            batch = self._api(endpoint + sep + "per_page=100&page=" + str(page))
            if not isinstance(batch, list):
                raise StudioError("GitHub 列表响应格式不符")
            results.extend(batch)
            if len(batch) < 100:
                return results
        raise StudioError("GitHub 分页过多，停止以避免不完整判断")

    def identity(self):
        info = self._api(self.base)
        user = self._api("user")
        return {"repository": info["full_name"], "id": info["id"],
                "account": user["login"], "can_write": bool(info.get("permissions", {}).get("push"))}

    def has_commit(self, commit):
        data = self._api(self.base + "/commits/" + commit, allow404=True)
        return bool(data and data.get("sha") == commit)

    def tag_commit(self, tag):
        data = self._api(self.base + "/git/ref/tags/" + quote(tag, safe=""), allow404=True)
        if not data:
            return None
        obj = data["object"]
        for _ in range(10):
            if obj["type"] == "commit":
                return obj["sha"]
            if obj["type"] != "tag":
                raise StudioError("标签未指向提交：" + tag)
            obj = self._api(self.base + "/git/tags/" + obj["sha"])["object"]
        raise StudioError("标签嵌套异常：" + tag)

    def create_tag(self, tag, commit):
        return self._api(self.base + "/git/refs", "POST",
                         {"ref": "refs/tags/" + tag, "sha": commit})

    def release_for_tag(self, tag):
        # The by-tag endpoint documents published releases only. Listing with a
        # push-capable identity also discovers drafts after a lost response.
        matches = [r for r in self._list(self.base + "/releases") if r.get("tag_name") == tag]
        if len(matches) > 1:
            raise StudioError("同一标签存在多个 Release，需人工核对")
        return matches[0] if matches else None

    def create_draft(self, plan):
        return self._api(self.base + "/releases", "POST", {
            "tag_name": plan["tag"], "target_commitish": plan["commit"],
            "name": plan["title"], "body": plan["notes"], "draft": True,
            "prerelease": "-rc." in plan["source_version"], "make_latest": "false",
        })

    def list_assets(self, release_id):
        assets = self._list(self.base + "/releases/{}/assets".format(release_id))
        for asset in assets:
            digest = asset.get("digest") or ""
            if re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                asset["sha256"] = digest[7:]
            elif asset.get("state") == "uploaded":
                body = self._api(self.base + "/releases/assets/" + str(asset["id"]),
                                 raw=True, accept="application/octet-stream")
                asset["sha256"] = hashlib.sha256(body).hexdigest()
        return assets

    def upload_asset(self, release_id, name, path, expected_sha256):
        body = Path(path).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected_sha256:
            raise StudioError("上传前冻结附件发生变化：" + name)
        endpoint = "https://uploads.github.com/" + self.base + "/releases/{}/assets?name={}".format(
            release_id, quote(name, safe=""))
        return self._api(endpoint, "POST", body, content_type="application/octet-stream")

    def publish(self, release_id):
        return self._api(self.base + "/releases/" + str(release_id), "PATCH",
                         {"draft": False, "make_latest": "false"})

    def latest(self):
        release = self._api(self.base + "/releases/latest", allow404=True)
        return release["tag_name"] if release else None

    def promote(self, release_id):
        return self._api(self.base + "/releases/" + str(release_id), "PATCH", {"make_latest": "true"})


class FakeRemote:
    """In-memory or JSON-persisted remote. fail_next simulates response loss.

    Operations: tag, draft, upload (or upload:filename), publish, promote.
    when='before' executes nothing; when='after' persists the successful action
    and then raises. Reopen the same state_path to test process-level recovery.
    """

    def __init__(self, state_path=None, repository="test-owner/test-book",
                 account="test-user", commits=None):
        self.state_path = Path(state_path) if state_path else None
        self.failures = []
        if self.state_path and self.state_path.exists():
            self.state = _json_read(self.state_path)
        else:
            self.state = {"repository": _repo(repository), "id": 1001, "account": account,
                          "can_write": True, "commits": list(commits or []), "tags": {},
                          "releases": {}, "latest": None, "writes": [], "next_id": 1}
            self.save()
        self.repository = self.state["repository"]

    def save(self):
        if self.state_path:
            _json_write(self.state_path, self.state)

    def fail_next(self, operation, when="after"):
        if when not in ("before", "after"):
            raise ValueError("when must be before or after")
        self.failures.append((operation, when))

    def _change(self, operation, callback):
        failure = next((f for f in self.failures if f[0] in (operation, operation.split(":")[0])), None)
        if failure:
            self.failures.remove(failure)
        if failure and failure[1] == "before":
            raise StudioError("模拟请求未执行：" + operation)
        result = callback()
        self.state["writes"].append(operation)
        self.save()
        if failure:
            raise StudioError("模拟远端成功但响应丢失：" + operation)
        return deepcopy(result)

    def identity(self):
        return {k: self.state[k] for k in ("repository", "id", "account", "can_write")}

    def has_commit(self, commit):
        return commit in self.state["commits"]

    def tag_commit(self, tag):
        return self.state["tags"].get(tag)

    def create_tag(self, tag, commit):
        def create():
            if tag in self.state["tags"]:
                raise StudioError("模拟远端标签已存在")
            if not self.has_commit(commit):
                raise StudioError("模拟远端缺少提交")
            self.state["tags"][tag] = commit
            return {"sha": commit}
        return self._change("tag", create)

    def release_for_tag(self, tag):
        return deepcopy(self.state["releases"].get(tag))

    def create_draft(self, plan):
        def create():
            if plan["tag"] in self.state["releases"]:
                raise StudioError("模拟远端 Release 已存在")
            release = {"id": self.state["next_id"], "tag_name": plan["tag"],
                       "target_commitish": plan["commit"], "name": plan["title"],
                       "body": plan["notes"], "draft": True,
                       "prerelease": "-rc." in plan["source_version"], "assets": [],
                       "published_at": None,
                       "html_url": "https://example.invalid/" + self.repository + "/releases/" + plan["tag"]}
            self.state["next_id"] += 1
            self.state["releases"][plan["tag"]] = release
            return release
        return self._change("draft", create)

    def _release(self, release_id):
        for release in self.state["releases"].values():
            if release["id"] == release_id:
                return release
        raise StudioError("模拟远端 Release 不存在")

    def list_assets(self, release_id):
        return deepcopy(self._release(release_id)["assets"])

    def upload_asset(self, release_id, name, path, expected_sha256):
        def upload():
            release = self._release(release_id)
            if not release["draft"]:
                raise StudioError("禁止向已公开模拟发行补传")
            if any(a["name"] == name for a in release["assets"]):
                raise StudioError("模拟远端同名附件已存在")
            digest = _digest(path)
            if digest != expected_sha256:
                raise StudioError("模拟上传前附件改变")
            asset = {"id": len(release["assets"]) + 1, "name": name, "sha256": digest,
                     "size": Path(path).stat().st_size, "state": "uploaded"}
            release["assets"].append(asset)
            return asset
        return self._change("upload:" + name, upload)

    def publish(self, release_id):
        def publish():
            release = self._release(release_id)
            release["draft"] = False
            release["published_at"] = _now()
            return release
        return self._change("publish", publish)

    def latest(self):
        return self.state["latest"]

    def promote(self, release_id):
        def promote():
            release = self._release(release_id)
            if release["draft"] or release["prerelease"]:
                raise StudioError("不能提升草稿或预发行")
            self.state["latest"] = release["tag_name"]
            return release
        return self._change("promote", promote)


def _preflight(plan_path, plan, remote, expected_repository=None, expected_account=None,
               write=False, allowed_repositories=None, test_mode=False):
    expected = _repo(expected_repository or plan["repository"])
    if expected.lower() != plan["repository"].lower():
        raise StudioError("显式目标与发布清单仓库不一致")
    if test_mode:
        allowed = {_repo(r).lower() for r in (allowed_repositories or [])}
        if not plan["is_test"] or expected.lower() not in allowed:
            raise StudioError("测试发布必须是虚构作品并命中明确的测试仓允许清单")
    identity = remote.identity()
    if identity["repository"].lower() != expected.lower():
        raise StudioError("当前远端仓库身份与显式目标不符")
    if plan.get("repository_id") is not None and str(identity["id"]) != str(plan["repository_id"]):
        raise StudioError("仓库稳定 ID 已变化")
    if expected_account and identity["account"].lower() != expected_account.lower():
        raise StudioError("当前登录账号与指定账号不符")
    if write and not identity.get("can_write"):
        raise StudioError("当前账号没有该仓库发布权限；不会自动扩权")
    execution_path = plan_path.parent / "execution.json"
    execution = _json_read(execution_path) if execution_path.exists() else None
    if execution:
        if execution.get("plan") != plan:
            raise StudioError("远端执行开始后的发布清单已被修改；停止恢复")
        if str(execution.get("repository_id")) != str(identity["id"]):
            raise StudioError("远端仓库稳定 ID 与首次执行不同")
        if execution.get("account", "").lower() != identity["account"].lower():
            raise StudioError("当前账号与首次执行不同，请核对后重新授权")
    return identity, execution


def _metadata_conflicts(plan, release):
    checks = [("tag_name", plan["tag"]), ("name", plan["title"]),
              ("body", plan["notes"]), ("prerelease", "-rc." in plan["source_version"])]
    return ["远端 Release 字段与清单不同：" + key for key, value in checks
            if (release.get(key) or "" if key == "body" else release.get(key)) != value]


def _asset_conflicts(plan, remote_assets):
    expected = {a["name"]: a for a in plan["assets"]}
    seen, errors = set(), []
    for asset in remote_assets:
        name = asset["name"]
        if name in seen:
            errors.append("远端附件重名：" + name)
        seen.add(name)
        if name not in expected:
            errors.append("远端有清单之外的附件：" + name)
        elif asset.get("state") != "uploaded":
            errors.append("远端附件未完整上传：" + name)
        elif asset.get("sha256") != expected[name]["sha256"] or asset.get("size") != expected[name]["size"]:
            errors.append("远端同名附件与清单内容不同：" + name)
    return errors, [name for name in expected if name not in seen]


def _published_receipt_conflicts(plan_path, plan, release):
    receipt_path = plan_path.parent / "receipt.json"
    if not receipt_path.exists():
        return []
    receipt = _json_read(receipt_path)
    if not receipt.get("published"):
        return []
    errors = ["已公开回执与清单不匹配：" + key for key in
              ("repository", "tag", "commit", "work_id", "kind", "source_version", "scope", "assets")
              if receipt.get(key) != plan.get(key)]
    if not release:
        errors.append("已公开 Release 在远端缺失；不会重新创建历史发行")
    elif release.get("draft"):
        errors.append("已公开 Release 在远端变为草稿；不会重新公开历史发行")
    elif str(release.get("id")) != str(receipt.get("release_id")):
        errors.append("已公开 Release 的远端 ID 已变化；停止恢复")
    return errors


def audit_release(plan_path, remote=None, *, expected_repository=None):
    """Read-only remote audit; complete publication and partial drafts differ."""
    plan_path, plan = _load_plan(plan_path)
    remote = remote or GhRemote(plan["repository"])
    identity, _ = _preflight(plan_path, plan, remote, expected_repository)
    tag_commit = remote.tag_commit(plan["tag"])
    release = remote.release_for_tag(plan["tag"])
    conflicts, missing = _published_receipt_conflicts(plan_path, plan, release), []
    if tag_commit is None:
        missing.append("tag")
    elif tag_commit != plan["commit"]:
        conflicts.append("远端标签指向其他提交")
    if plan["kind"] == "pdf" and remote.tag_commit(plan["source_version"]) != plan["commit"]:
        conflicts.append("PDF 正文来源标签不存在或提交不符")
    if release:
        conflicts += _metadata_conflicts(plan, release)
        errors, assets_missing = _asset_conflicts(plan, remote.list_assets(release["id"]))
        conflicts += errors
        missing += ["asset:" + name for name in assets_missing]
    else:
        missing.append("release")
    status = "published" if release and not release["draft"] else "draft" if release else "not_started"
    return {"ok": not conflicts and not missing, "status": status,
            "published": status == "published", "repository": identity["repository"],
            "tag": plan["tag"], "commit": tag_commit,
            "release_id": release["id"] if release else None,
            "latest": remote.latest(), "conflicts": conflicts, "missing": missing,
            "plan_path": str(plan_path)}


def publish_release(plan_path, remote=None, *, expected_repository, authorized=False,
                    expected_account=None, allowed_repositories=None, test_mode=False):
    """Publish/resume a frozen plan. Authorization is explicit, never inferred.

    Returns ok=False, published=True when publication is verified but promotion
    conflicts. Other conflicts or uncertain requests raise StudioError; receipt
    and execution records preserve the last known facts for audit/resume.
    """
    if not authorized:
        raise StudioError("尚未明确授权此发布动作；只可准备或审计")
    if not expected_repository:
        raise StudioError("发布必须显式指定目标仓库")
    plan_path, plan = _load_plan(plan_path)
    remote = remote or GhRemote(plan["repository"])
    identity, execution = _preflight(plan_path, plan, remote, expected_repository,
                                    expected_account, True, allowed_repositories, test_mode)
    if not remote.has_commit(plan["commit"]):
        raise StudioError("候选提交不在目标远端；请先按授权正常合入，不自动 push")
    tag = remote.tag_commit(plan["tag"])
    if tag and tag != plan["commit"]:
        raise StudioError("远端标签指向其他提交；不会移动标签")
    if plan["kind"] == "pdf" and remote.tag_commit(plan["source_version"]) != plan["commit"]:
        raise StudioError("PDF 正文来源标签不存在或提交不符")
    release = remote.release_for_tag(plan["tag"])
    historical_conflicts = _published_receipt_conflicts(plan_path, plan, release)
    if historical_conflicts:
        raise StudioError("；".join(historical_conflicts))
    if release:
        errors = _metadata_conflicts(plan, release)
        conflicts, missing = _asset_conflicts(plan, remote.list_assets(release["id"]))
        errors += conflicts
        if not release["draft"] and missing:
            errors.append("正式发行附件缺失；不对已公开版本补传")
        if errors:
            raise StudioError("；".join(errors))
    if not release or release["draft"]:
        for asset in plan["assets"]:
            _frozen_asset(plan_path, asset)
    execution_path = plan_path.parent / "execution.json"
    receipt_path = plan_path.parent / "receipt.json"
    if not execution:
        execution = {"plan": deepcopy(plan), "repository_id": identity["id"],
                     "account": identity["account"], "started_at": _now(), "last_step": "preflight"}
    _json_write(execution_path, execution)  # durable BEFORE any remote mutation
    receipt = {"repository": plan["repository"], "tag": plan["tag"], "commit": plan["commit"],
               "work_id": plan["work_id"], "kind": plan["kind"],
               "source_version": plan["source_version"], "scope": deepcopy(plan["scope"]),
               "published": bool(release and not release["draft"]), "promotion": "not_requested"}
    if receipt_path.exists():
        previous = _json_read(receipt_path)
        if previous.get("published"):
            receipt.update(previous)  # never rewrite a known publication as unissued

    def perform(step, function, *args):
        if _json_read(plan_path) != plan:
            raise StudioError("执行期间发布清单改变，停止远端写入")
        execution["last_step"] = step
        execution["attempted_at"] = _now()
        _json_write(execution_path, execution)
        return function(*args)

    try:
        if tag is None:
            perform("create_tag", remote.create_tag, plan["tag"], plan["commit"])
        if remote.tag_commit(plan["tag"]) != plan["commit"]:
            raise StudioError("创建后标签核对失败")
        if release is None:
            perform("create_draft", remote.create_draft, plan)
            release = remote.release_for_tag(plan["tag"])
        if not release:
            raise StudioError("无法定位远端草稿；请 audit 后恢复")
        receipt["release_id"] = release["id"]
        for asset in plan["assets"]:
            current = remote.list_assets(release["id"])
            errors, missing = _asset_conflicts(plan, current)
            if errors:
                raise StudioError("；".join(errors))
            if asset["name"] in missing:
                if not release["draft"]:
                    raise StudioError("已公开发行缺失附件；不能补传")
                frozen = _frozen_asset(plan_path, asset)
                perform("upload:" + asset["name"], remote.upload_asset, release["id"],
                        asset["name"], frozen, asset["sha256"])
        before = audit_release(plan_path, remote, expected_repository=expected_repository)
        if not before["ok"]:
            raise StudioError("公开前核对失败：" + "; ".join(before["conflicts"] + before["missing"]))
        if before["status"] == "draft":
            perform("publish", remote.publish, release["id"])
        verified = audit_release(plan_path, remote, expected_repository=expected_repository)
        if not verified["ok"] or not verified["published"]:
            raise StudioError("公开结果尚未核实；保留现场后 audit")
        remote_release = remote.release_for_tag(plan["tag"])
        receipt.update({"published": True, "verified_at": _now(), "status": "published",
                        "published_at": remote_release.get("published_at"),
                        "url": remote_release.get("html_url"), "assets": plan["assets"]})
        receipt.pop("error", None)
        _json_write(receipt_path, receipt)
        if plan["promote"]:
            latest = remote.latest()
            if latest == plan["tag"]:
                receipt["promotion"] = "succeeded"
            elif latest != plan["expected_previous"]:
                receipt.update({"promotion": "blocked", "error": "推荐版本已变化，保留已公开发行，不自动回退",
                                "actual_latest": latest})
            else:
                perform("promote", remote.promote, release["id"])
                if remote.latest() != plan["tag"]:
                    raise StudioError("推荐入口更新结果不明，需 audit")
                receipt["promotion"] = "succeeded"
            _json_write(receipt_path, receipt)
        return {"ok": receipt["promotion"] != "blocked", **receipt,
                "plan_path": str(plan_path), "receipt_path": str(receipt_path)}
    except (StudioError, OSError) as exc:
        receipt.update({"error": str(exc), "last_step": execution.get("last_step"),
                        "checked_at": _now(), "status": "published" if receipt["published"] else "uncertain"})
        _json_write(receipt_path, receipt)
        if isinstance(exc, StudioError):
            raise
        raise StudioError("发布中断；清单和现场已保留：{}".format(exc))


def resume_release(plan_path, remote=None, **kwargs):
    """The same operation resumes by inspecting remote facts, not replaying writes."""
    return publish_release(plan_path, remote, **kwargs)
