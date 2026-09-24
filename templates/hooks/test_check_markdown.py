import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('check_markdown.py')

class HookExampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='book hook ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'hook-demo').mkdir()
        self.file = self.root / 'hook-demo' / 'notes.md'
        self.file.write_text('# 标题\n\n正文。\n', encoding='utf-8')

    def event(self, path=None, **updates):
        value = {'hook_event_name': 'PostToolUse', 'tool_name': 'Write',
                 'tool_input': {'file_path': str(path or self.file)}}
        value.update(updates)
        return value

    def run_hook(self, event, project=True, raw=False):
        environment = os.environ.copy()
        environment.pop('CLAUDE_PROJECT_DIR', None)
        if project:
            environment['CLAUDE_PROJECT_DIR'] = str(self.root)
        payload = event if raw else json.dumps(event, ensure_ascii=True)
        return subprocess.run([sys.executable, str(SCRIPT)], input=payload.encode('utf-8'),
                              capture_output=True, env=environment, timeout=5)

    def test_valid_read_only(self):
        before = self.file.read_bytes()
        result = self.run_hook(self.event())
        self.assertEqual(result.returncode, 0)
        self.assertIn('检查通过', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
        self.assertEqual(self.file.read_bytes(), before)

    def test_missing_title_and_newline(self):
        self.file.write_text('正文', encoding='utf-8')
        result = self.run_hook(self.event())
        message = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
        self.assertIn('缺少一级标题', message)
        self.assertIn('没有换行', message)
        self.assertEqual(result.returncode, 0)

    def test_empty_heading_does_not_borrow_next_line(self):
        self.file.write_text('#\n正文。\n', encoding='utf-8')
        result = self.run_hook(self.event())
        message = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
        self.assertIn('缺少一级标题', message)

    def test_edit_event(self):
        self.assertTrue(self.run_hook(self.event(tool_name='Edit')).stdout)

    def test_unrelated_tool(self):
        self.assertEqual(self.run_hook(self.event(tool_name='Bash')).stdout, b'')

    def test_unrelated_event(self):
        self.assertEqual(self.run_hook(self.event(hook_event_name='PreToolUse')).stdout, b'')

    def test_non_markdown(self):
        p = self.root / 'hook-demo' / 'data.txt'
        p.write_text('sample')
        self.assertEqual(self.run_hook(self.event(p)).stdout, b'')

    def test_outside_demo(self):
        p = self.root / 'private.md'
        p.write_text('DO_NOT_ECHO')
        result = self.run_hook(self.event(p))
        self.assertEqual(result.stdout, b'')
        self.assertNotIn(b'DO_NOT_ECHO', result.stderr)

    def test_symlink_outside_demo(self):
        p = self.root / 'private.md'
        p.write_text('DO_NOT_ECHO')
        link = self.root / 'hook-demo' / 'link.md'
        link.symlink_to(p)
        self.assertEqual(self.run_hook(self.event(link)).stdout, b'')

    def test_no_shell_interpolation(self):
        p = self.root / 'hook-demo' / 'quote\" $(touch bad).md'
        p.write_text('# Safe\n')
        result = self.run_hook(self.event(p))
        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.root / 'bad').exists())

    def test_bad_json_is_reported(self):
        result = self.run_hook('not-json SECRET', raw=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(b'SECRET', result.stderr)

    def test_missing_project_fails(self):
        self.assertEqual(self.run_hook(self.event(), project=False).returncode, 1)

    def test_missing_file_fails(self):
        self.assertEqual(self.run_hook(self.event(self.root / 'hook-demo' / 'missing.md')).returncode, 1)

    def test_size_limit(self):
        self.file.write_bytes(b'x' * (1024 * 1024 + 1))
        self.assertEqual(self.run_hook(self.event()).returncode, 1)

    def test_invalid_utf8_is_reported(self):
        self.file.write_bytes(b'\xff\xfe')
        self.assertEqual(self.run_hook(self.event()).returncode, 1)

if __name__ == '__main__':
    unittest.main()
