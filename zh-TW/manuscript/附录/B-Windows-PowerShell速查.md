<a id="附录-bwindows-powershell-速查"></a>
# 附錄 B：Windows PowerShell 速查

> 用法：按 `Win + X` 選 "終端"（Windows 11）或 "PowerShell"。**本書不推薦 WSL / CMD——統一用 PowerShell**。

<a id="本章地图一眼看全貌"></a>
### 本章地圖（一眼看全貌）

本章圖解：[PowerShell 的輸入位置](#提示符符号速读)。

<a id="最常用-15-个命令"></a>
## 最常用 15 個命令

| 命令 | 幹什麼 | 例 |
|-----|-------|---|
| `pwd` | 看我在哪個資料夾 | `pwd` |
| `ls` | 列當前資料夾 | `ls` |
| `ls -Force` | 連隱藏檔案都列 | `ls -Force` |
| `cd 文件夹名` | 進去 | `cd Documents` |
| `cd ..` | 上一層 | `cd ..` |
| `cd ~` | 回使用者資料夾 | `cd ~` |
| `mkdir 名字` | 建資料夾 | `mkdir notes` |
| `New-Item -ItemType File 名字` | 建空檔案；已存在時先檢查 | `New-Item -ItemType File todo.md` |
| `cp 源 目标` | 複製 | `cp a.txt b.txt` |
| `mv 源 目标` | 移動 / 重新命名 | `mv a.txt b.txt` |
| `rm 文件` | 刪除（**小心**，不進回收站） | `rm old.txt` |
| `Remove-Item -Recurse 文件夹` | 刪資料夾及內容，不進回收站 | `Remove-Item -Recurse temp` |
| `explorer .` | 在資源管理器開啟當前 | `explorer .` |
| `cls` | 清屏 | `cls` |
| `notepad 文件` | 用記事本開啟 | `notepad todo.md` |

<a id="最常用快捷键"></a>
## 最常用快捷鍵

| 快捷鍵 | 作用 |
|-------|------|
| `Tab` | 自動補全 |
| `↑` / `↓` | 翻歷史 |
| `Home` | 游標跳行首 |
| `End` | 游標跳行尾 |
| `Ctrl+C` | 中斷 |
| `Ctrl+L` 或 `cls` | 清屏 |
| `Ctrl+Shift+T` | 新標籤頁（Windows Terminal 預設設定） |
| `Ctrl+Shift+N` | 新視窗（Windows Terminal 預設設定） |
| `Ctrl+加号 / 减号` | 字號 |

<a id="提示符符号速读"></a>
## 提示符符號速讀

- `>`（如 `PS C:\Users\你>`）：PowerShell 等你打字
- `PS` = PowerShell
- Windows 原生路徑通常用 **反斜槓 `\`**；PowerShell 的檔案路徑也常接受 `/`，但外部程式引數要另查

<!-- diagram: FIG-032 -->
![PowerShell 的輸入位置](../../../assets/illustrations/FIG-032/revisions/r02/zh-CN.png)

*圖：在 PowerShell 先看當前位置，再輸入命令*
<!-- /diagram: FIG-032 -->

<a id="常见错误翻译"></a>
## 常見錯誤翻譯

| 看到 | 意思 | 怎麼辦 |
|-----|-----|-------|
| `The term 'xxx' is not recognized` | 拼寫、安裝狀態或 PATH 等不符 | 確認命令環境與 `Get-Command xxx` 的結果，再按官方安裝說明處理 |
| `Cannot find path 'xxx' because it does not exist` | 路徑錯 | `pwd` 和 `ls` 核查 |
| `Access to the path 'xxx' is denied` | 目標訪問被拒絕 | 先核對路徑、賬戶許可權與檔案佔用，不把管理員模式當通用修復 |
| `... is currently disabled on this system` | 指令碼執行政策限制 | 先用 `Get-ExecutionPolicy -List` 檢視各作用域，核對指令碼來源與組織策略；不直接修改全機策略 |
| `... cannot be loaded because running scripts is disabled` | 同上 | 同上 |

<a id="windows-特别要注意的路径差异"></a>
## Windows 特別要注意的路徑差異

- 原生路徑通常用 **反斜槓** `\`；PowerShell 檔案路徑也常接受 `/`
- 磁碟機代號 `C:\` `D:\`——Mac/Linux 沒有
- **空格路徑用引號**：`cd "Program Files"`
- **使用者資料夾**：通常為 `C:\Users\你的名字`；桌面可能由 OneDrive 重定向，用 `Set-Location ([Environment]::GetFolderPath('Desktop'))` 進入實際桌面

<a id="powershell-的别名"></a>
## PowerShell 的"別名"

很多 PowerShell 原本的命令有 Unix 風格別名，方便跨平臺使用者：

| PowerShell 原生 | 別名（Mac / Unix 風格） |
|---------------|----------------------|
| `Get-ChildItem` | `ls`（也支援 `dir`） |
| `Set-Location` | `cd` |
| `Copy-Item` | `cp`（也支援 `copy`） |
| `Move-Item` | `mv`（也支援 `move`） |
| `Remove-Item` | `rm`（也支援 `del`） |

本表保留常見別名幫助認讀；**別名相同不代表引數與 Unix 命令相同**。需要引數時優先看對應 PowerShell 原生命令說明，不照搬 `rm -rf`、`ls -la`。

<a id="一些我希望早点知道"></a>
## 一些"我希望早點知道"

- **拖檔案進終端** → 自動填路徑（和 Mac 一樣）
- **管理員許可權**只用於已經確認需要且有權執行的管理任務；日常練習用普通視窗
- **`dir`** 也能用（老 CMD 風格，PowerShell 相容）
- **`clip`** 命令 → `echo "hello" | clip` 把輸出複製到剪貼簿

來源：[Windows Terminal 按鍵](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions)、[PowerShell 執行策略](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy)。快捷鍵可被使用者重設。
