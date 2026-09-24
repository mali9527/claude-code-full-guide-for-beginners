#!/usr/bin/env python3
"""Read-only PostToolUse teaching example: inspect project/hook-demo/*.md."""
import json
import os
from pathlib import Path
import re
import sys

MAX_BYTES = 1024 * 1024

def inspect_event(event, project_dir):
    if not isinstance(event, dict):
        raise ValueError('hook input must be an object')
    if event.get('hook_event_name') != 'PostToolUse':
        return None
    if event.get('tool_name') not in ('Write', 'Edit'):
        return None
    tool_input = event.get('tool_input')
    if not isinstance(tool_input, dict):
        raise ValueError('missing tool_input')
    raw_path = tool_input.get('file_path')
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError('missing file_path')
    if not project_dir:
        raise ValueError('missing CLAUDE_PROJECT_DIR')
    project = Path(project_dir).resolve(strict=True)
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        raise ValueError('expected an absolute file_path')
    target = candidate.resolve(strict=True)
    try:
        relative = target.relative_to(project)
    except ValueError:
        return None
    if len(relative.parts) != 2 or relative.parts[0] != 'hook-demo':
        return None
    if target.suffix.lower() != '.md' or not target.is_file():
        return None
    with target.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('sample file exceeds 1 MiB')
    contents = raw.decode('utf-8-sig')
    problems = []
    if not re.search(r'^#[ \t]+\S', contents, re.MULTILINE):
        problems.append('缺少一级标题')
    if not contents.endswith('\n'):
        problems.append('文件末尾没有换行')
    verdict = '；'.join(problems) if problems else '标题与末尾换行检查通过'
    message = '本书 Hook 样例：' + verdict + '。仅作提示，未修改文件；这不是全文质量审校。'
    return {'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': message}}

def main():
    try:
        event = json.loads(sys.stdin.buffer.read().decode('utf-8-sig'))
        result = inspect_event(event, os.environ.get('CLAUDE_PROJECT_DIR'))
        if result is not None:
            print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, TypeError) as error:
        # Never echo the event: it can contain user file contents or credentials.
        print('book hook: input or sample file check failed (' + type(error).__name__ + ')', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
