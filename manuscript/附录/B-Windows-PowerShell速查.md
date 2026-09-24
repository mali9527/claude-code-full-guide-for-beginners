# 附录 B：Windows PowerShell 速查

> 用法：按 `Win + X` 选 "终端"（Windows 11）或 "PowerShell"。**本书不推荐 WSL / CMD——统一用 PowerShell**。

### 本章地图（一眼看全貌）

本章图解：[PowerShell 的输入位置](#提示符符号速读)。

## 最常用 15 个命令

| 命令 | 干什么 | 例 |
|-----|-------|---|
| `pwd` | 看我在哪个文件夹 | `pwd` |
| `ls` | 列当前文件夹 | `ls` |
| `ls -Force` | 连隐藏文件都列 | `ls -Force` |
| `cd 文件夹名` | 进去 | `cd Documents` |
| `cd ..` | 上一层 | `cd ..` |
| `cd ~` | 回用户文件夹 | `cd ~` |
| `mkdir 名字` | 建文件夹 | `mkdir notes` |
| `New-Item -ItemType File 名字` | 建空文件；已存在时先检查 | `New-Item -ItemType File todo.md` |
| `cp 源 目标` | 复制 | `cp a.txt b.txt` |
| `mv 源 目标` | 移动 / 重命名 | `mv a.txt b.txt` |
| `rm 文件` | 删除（**小心**，不进回收站） | `rm old.txt` |
| `Remove-Item -Recurse 文件夹` | 删文件夹及内容，不进回收站 | `Remove-Item -Recurse temp` |
| `explorer .` | 在资源管理器打开当前 | `explorer .` |
| `cls` | 清屏 | `cls` |
| `notepad 文件` | 用记事本打开 | `notepad todo.md` |

## 最常用快捷键

| 快捷键 | 作用 |
|-------|------|
| `Tab` | 自动补全 |
| `↑` / `↓` | 翻历史 |
| `Home` | 光标跳行首 |
| `End` | 光标跳行尾 |
| `Ctrl+C` | 中断 |
| `Ctrl+L` 或 `cls` | 清屏 |
| `Ctrl+Shift+T` | 新标签页（Windows Terminal 默认设置） |
| `Ctrl+Shift+N` | 新窗口（Windows Terminal 默认设置） |
| `Ctrl+加号 / 减号` | 字号 |

## 提示符符号速读

- `>`（如 `PS C:\Users\你>`）：PowerShell 等你打字
- `PS` = PowerShell
- Windows 原生路径通常用 **反斜杠 `\`**；PowerShell 的文件路径也常接受 `/`，但外部程序参数要另查

<!-- diagram: FIG-032 -->
![PowerShell 的输入位置](../../assets/illustrations/FIG-032/revisions/r02/zh-CN.png)

*图：在 PowerShell 先看当前位置，再输入命令*
<!-- /diagram: FIG-032 -->

## 常见错误翻译

| 看到 | 意思 | 怎么办 |
|-----|-----|-------|
| `The term 'xxx' is not recognized` | 拼写、安装状态或 PATH 等不符 | 确认命令环境与 `Get-Command xxx` 的结果，再按官方安装说明处理 |
| `Cannot find path 'xxx' because it does not exist` | 路径错 | `pwd` 和 `ls` 核查 |
| `Access to the path 'xxx' is denied` | 目标访问被拒绝 | 先核对路径、账户权限与文件占用，不把管理员模式当通用修复 |
| `... is currently disabled on this system` | 脚本执行政策限制 | 先用 `Get-ExecutionPolicy -List` 查看各作用域，核对脚本来源与组织策略；不直接修改全机策略 |
| `... cannot be loaded because running scripts is disabled` | 同上 | 同上 |

## Windows 特别要注意的路径差异

- 原生路径通常用 **反斜杠** `\`；PowerShell 文件路径也常接受 `/`
- 盘符 `C:\` `D:\`——Mac/Linux 没有
- **空格路径用引号**：`cd "Program Files"`
- **用户文件夹**：通常为 `C:\Users\你的名字`；桌面可能由 OneDrive 重定向，用 `Set-Location ([Environment]::GetFolderPath('Desktop'))` 进入实际桌面

## PowerShell 的"别名"

很多 PowerShell 原本的命令有 Unix 风格别名，方便跨平台用户：

| PowerShell 原生 | 别名（Mac / Unix 风格） |
|---------------|----------------------|
| `Get-ChildItem` | `ls`（也支持 `dir`） |
| `Set-Location` | `cd` |
| `Copy-Item` | `cp`（也支持 `copy`） |
| `Move-Item` | `mv`（也支持 `move`） |
| `Remove-Item` | `rm`（也支持 `del`） |

本表保留常见别名帮助认读；**别名相同不代表参数与 Unix 命令相同**。需要参数时优先看对应 PowerShell 原生命令说明，不照搬 `rm -rf`、`ls -la`。

## 一些"我希望早点知道"

- **拖文件进终端** → 自动填路径（和 Mac 一样）
- **管理员权限**只用于已经确认需要且有权执行的管理任务；日常练习用普通窗口
- **`dir`** 也能用（老 CMD 风格，PowerShell 兼容）
- **`clip`** 命令 → `echo "hello" | clip` 把输出复制到剪贴板

来源：[Windows Terminal 按键](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions)、[PowerShell 执行策略](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy)。快捷键可被用户重设。

<!-- studio:nav -->
← [附录 A：Mac 终端速查](A-Mac%E7%BB%88%E7%AB%AF%E9%80%9F%E6%9F%A5.md) · [目录](../../README.md) · [附录 C：常用 Slash 命令速查](C-Slash%E5%91%BD%E4%BB%A4%E5%85%A8%E8%A1%A8.md) →
<!-- /studio:nav -->
