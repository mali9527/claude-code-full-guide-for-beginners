# 第 23 章配套：只读 Markdown Hook

这是本书原创教学样例。只检查项目根目录 `hook-demo/` 中直接存放的 `.md` 文件有没有一级标题、末尾换行，不修改文件、不联网、不运行文件里的内容。

它演示的是 `PostToolUse` 输入与反馈，不是完整 Markdown 检查器，更不是防止其它程序读写文件的安全边界。脚本自行检查会通过，但你还需要在自己的 Claude Code 会话中确认事件确实触发。

## 准备与安装

1. 将此目录中的 `check_markdown.py` 放到练习项目的 `templates/hooks/`，保持这一相对路径。
2. 你需要 Python 3。Mac 运行 `python3 --version`，Windows PowerShell 运行 `py -3 --version`。找不到时可先只读第 23 章，或从 [Python 官方下载页](https://www.python.org/downloads/) 安装；本样例不需要第三方 Python 包。
3. 在练习项目内建 `hook-demo` 文件夹。
4. 打开该项目的 `.claude/settings.local.json`。文件存在时先保留副本；把下面的 `hooks` 条目合并进去，**不要用整段示例覆盖现有配置**。同一事件原本有其它条目时保留它们。配置有组织策略限制时按策略处理。

Mac 的完整最小配置：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/templates/hooks/check_markdown.py"],
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Windows 使用同样的结构，将 `command` 改为 `py`，将 `args` 改为下面的数组：

```json
["-3", "${CLAUDE_PROJECT_DIR}/templates/hooks/check_markdown.py"]
```

这是当前 Hook 支持的直接执行形式：程序名和参数分开，不让 shell 解释文件名。`${CLAUDE_PROJECT_DIR}` 由 Claude Code 替换为启动项目路径，含空格的路径仍作为一个参数传入。没有 `py`、但 `python --version` 确认是 Python 3 的 Windows 环境，可用 `command: "python"`，参数里去掉 `-3`。

设置文件的格式可以在本地检查，不必上传在线校验站：Mac 使用 `python3 -m json.tool .claude/settings.local.json`；Windows 使用 `py -3 -m json.tool .claude/settings.local.json`。确认是有效 JSON 后，重新启动 Claude Code，用 `/hooks` 查看生效条目。

## 用一份事件输入验证脚本

先用文本编辑器新建 `hook-demo/notes.md`，内容为一级标题 `# 练习` 和一小段正文，并确保文件末尾有换行。新建 `hook-event.json`，按下面示例填写，`file_path` 换成该文件的**绝对路径**。Windows 路径里的反斜杠在 JSON 中需要写两次，也可以在这个手动样例中用正斜杠；Claude Code 的真实事件会生成平台对应的路径。

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {"file_path": "/你的练习项目/hook-demo/notes.md"}
}
```

Mac，仍在项目目录：

```bash
CLAUDE_PROJECT_DIR="$PWD" python3 templates/hooks/check_markdown.py < hook-event.json
```

Windows PowerShell：

```powershell
$env:CLAUDE_PROJECT_DIR = (Get-Location).Path
$savedOutputEncoding = $OutputEncoding
try {
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    Get-Content -Raw -Encoding UTF8 hook-event.json | py -3 templates/hooks/check_markdown.py
} finally {
    $OutputEncoding = $savedOutputEncoding
}
```

Windows PowerShell 5.1 将文本经管道送给外部程序时，默认编码可能丢失中文路径。上面的设置只在这次调用中采用 UTF-8，然后恢复原值；只写 `Get-Content -Encoding UTF8` 不能控制后半段管道编码。此处是手动测试输入的处理，Claude Code 真实 Hook 事件不经过这段 PowerShell 管道。[PowerShell 编码说明](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1)

输出是包含 `hookSpecificOutput.additionalContext` 的 JSON。中文可能显示为 `\u` 转义，这是正常的 JSON 表达，Claude Code 解析后会得到中文。去掉练习文件的一级标题再运行，反馈应改变；脚本不会替你修复文件。输入结构错误、文件不存在或超过 1 MiB 时会返回错误，且不会把原始事件中的文件内容打印出来。

## 再验证真实 Hook

在 Claude Code 中明确要求：“用 Write 工具在 `hook-demo/notes.md` 写一段没有一级标题的练习文字，观察本书 Hook 的反馈，不要自动修复。”

反馈供 Claude 读取，不保证在界面中单独显示为一条聊天消息。需要查证时以 `claude --debug-file hook-debug.log` 启动，再检查日志里的本书 Hook 名称、执行结果与输出；日志可能包含项目内容，勿公开整个日志。若 Claude 使用 shell 写文件，`Write|Edit` 不会匹配这次操作，需换成对应工具重试，不能据此说 Hook 失效。

脚本返回码 0 表示样例正常完成或事件被跳过；本样例的返回码 1 表示输入/文件检查出错，不把它冒充为成功。它不使用阻塞返回码，不撤销已完成的写入。

## 撤销与维护

移除你新增的这一条 Hook，保留原来其它设置，再重启会话。然后可删除练习文件和这份脚本。不要删除整个 `.claude` 目录。

开发验证可运行 `python3 -m unittest discover -s templates/hooks -p 'test_*.py' -v`。自动测试覆盖有效输入、缺少标题/换行、Edit 事件、跳过无关事件、路径边界、符号链接、特殊文件名、错误 JSON、缺失文件和过大文件等。

核验依据：[Hook 输入、PostToolUse 与直接执行形式](https://code.claude.com/docs/en/hooks)、[Hook 入门与退出码](https://code.claude.com/docs/en/hooks-guide)。核验日期：2026-09-25。样例脚本已在 macOS Python 3 本地测试；Windows 命令与真实 Claude 事件需要在对应环境验收。
