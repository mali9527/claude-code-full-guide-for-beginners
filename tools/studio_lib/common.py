from pathlib import Path
import os
import re
import subprocess
import tempfile
import yaml

class StudioError(Exception):
    pass

def load_yaml(path):
    p = Path(path)
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as e:
        raise StudioError("{}: {}".format(p, e))

def atomic_write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="."+p.name+".", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def dump_yaml(path, value):
    atomic_write(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False))

def safe_path(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise StudioError("必须是书仓内的相对路径：{}".format(relative))
    p = root / relative
    try:
        p.resolve().relative_to(root)
    except ValueError:
        raise StudioError("路径越界：{}".format(relative))
    return p

def run_git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], text=True,
                            capture_output=True, env={**os.environ, "GIT_OPTIONAL_LOCKS":"0"})
    if result.returncode:
        raise StudioError("Git {}：{}".format(" ".join(args[:2]), result.stderr.strip()))
    return result.stdout.strip()

def git_commit(root, ref="HEAD"):
    if not isinstance(ref, str) or not ref or ref.startswith("-"):
        raise StudioError("无效 Git 引用")
    return run_git(root, "rev-parse", "--verify", ref+"^{commit}")

def slug(text):
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = text.replace(chr(96), "")
    text = "".join(c for c in text if c.isalnum() or c in " _-")
    return text.replace(" ", "-")

def stripped_generated(text):
    return re.sub(r"<!-- studio:nav -->.*?<!-- /studio:nav -->", "", text, flags=re.S).strip()
