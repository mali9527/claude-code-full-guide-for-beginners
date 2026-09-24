# 附录 A：Mac 终端速查

> 用法：打开 终端.app（Spotlight 搜 "终端"），按速查表敲命令。

### 本章地图（一眼看全貌）

本章图解：[Mac 终端的输入位置](#提示符符号速读)。

## 最常用 15 个命令

| 命令 | 干什么 | 例 |
|-----|-------|---|
| `pwd` | 看我现在在哪个文件夹 | `pwd` |
| `ls` | 列当前文件夹里的东西 | `ls` |
| `ls -la` | 连隐藏文件和详细信息都列 | `ls -la` |
| `cd 文件夹名` | 进入某个文件夹 | `cd Documents` |
| `cd ..` | 上一层文件夹 | `cd ..` |
| `cd ~` | 回自己的用户文件夹（家） | `cd ~` |
| `cd -` | 回上次那个文件夹 | `cd -` |
| `mkdir 名字` | 建一个新文件夹 | `mkdir notes` |
| `touch 名字` | 文件不存在时新建；存在时更新时间戳 | `touch todo.md` |
| `cp 源 目标` | 复制 | `cp a.txt b.txt` |
| `mv 源 目标` | 移动 / 重命名 | `mv a.txt b.txt` |
| `rm 文件` | 删除（**小心**，不进回收站） | `rm old.txt` |
| `rm -rf 文件夹` | 删文件夹及里面所有内容（**最危险**，再三确认） | `rm -rf temp/` |
| `open .` | 在 Finder 打开当前文件夹 | `open .` |
| `clear` | 清屏 | `clear` |

## 最常用快捷键

| 快捷键 | 作用 |
|-------|------|
| `Tab` | 自动补全文件名 / 命令 |
| `↑` / `↓` | 翻命令历史 |
| `Ctrl+A` | 光标跳到行首 |
| `Ctrl+E` | 光标跳到行尾 |
| `Ctrl+C` | 中断当前运行的命令 |
| `Ctrl+D` | 空输入时向 shell 发送结束信号，通常退出；程序内行为另看 |
| `Ctrl+L` | 清屏（等同 `clear`） |
| `Cmd+T` | 新标签页 |
| `Cmd+N` | 新窗口 |
| `Cmd+K` | 清除终端显示与回滚缓冲；不删除 shell 命令历史文件 |
| `Cmd+加号 / 减号` | 字号变大 / 变小 |

## 提示符符号速读

- `%`（zsh，新版 Mac 默认）：等着你打字
- `$`（bash，老 Mac）：一样意思
- 看到 `~` = 你在自己的用户文件夹

<!-- diagram: FIG-031 -->
![Mac 终端的输入位置](../../assets/illustrations/FIG-031/revisions/r02/zh-CN.png)

*图：在 Mac 终端先看当前目录，再输入命令*
<!-- /diagram: FIG-031 -->

## 常见错误翻译

| 看到 | 意思 | 怎么办 |
|-----|-----|-------|
| `command not found: xxx` | 当前 shell 找不到命令 | 先查拼写、安装状态与 PATH，再按该程序官方说明处理 |
| `No such file or directory` | 找不到这个文件 / 文件夹 | `pwd` 看你在哪、`ls` 看有没有 |
| `Permission denied` | 权限不够 | 先核对路径、文件归属与任务范围；不要默认提权 |
| `zsh: parse error` | 命令打错了（缺引号 / 括号） | 仔细看命令，重新敲 |
| `Operation not permitted` | 系统拒绝操作，可能涉及隐私授权、文件标志或系统保护 | 先查目标路径与系统提示，不默认关闭 SIP 或扩大权限 |

## 一些"我希望早点知道"

- **拖文件进终端** → 自动填入完整路径（省去手打）
- **`ls | less`**（带竖线）→ 列表太长时分页看，按 `q` 退出
- **`!!`** → 重复上一条命令（执行前重新看清完整命令，不要用它盲目补管理员权限）
- **`cd`** 单独一个 → 等同 `cd ~`
- **`open 文件.pdf`** → 用默认程序打开这个文件

来源：[Apple 终端快捷键](https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac)。

<!-- studio:nav -->
← [第 27 章：下一步路线——读完书只是起点](../part6-%E8%9E%8D%E5%85%A5%E6%97%A5%E5%B8%B8/27-%E4%B8%8B%E4%B8%80%E6%AD%A5%E8%B7%AF%E7%BA%BF.md) · [目录](../../README.md) · [附录 B：Windows PowerShell 速查](B-Windows-PowerShell%E9%80%9F%E6%9F%A5.md) →
<!-- /studio:nav -->
