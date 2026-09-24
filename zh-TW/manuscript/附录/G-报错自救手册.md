<a id="附录-g常见报错与自救手册"></a>
# 附錄 G：常見報錯與自救手冊

> 按關鍵詞搜。每條格式：**看到什麼 → 最可能原因 → 怎麼辦**。

<a id="本章地图一眼看全貌"></a>
### 本章地圖（一眼看全貌）

本章圖解：[報錯時先收集這四樣](#通用排查顺序)。

<a id="安装阶段"></a>
## 安裝階段

<a id="command-not-found-claude"></a>
### `command not found: claude`

**原因**：Claude Code 沒裝；或裝了但 PATH 沒更新。
**怎麼辦**：
- 先回第 2 章確認原來的安裝方式，不要混裝；原生安裝不需要 Node.js
- 關掉終端重開（讓 PATH 生效）
- 確認 `which claude`（Mac）/ `Get-Command claude`（Windows PowerShell）能找到

<a id="eacces-permission-denied安装时"></a>
### `EACCES: permission denied`（安裝時）

**原因**：npm 全域性安裝時許可權不夠。
**怎麼辦**：
- 不要補 `sudo` 重跑 npm 安裝；官方不建議這樣做
- 若 `claude` 已能執行，用 `claude doctor` 檢查；程式不存在時，先按安裝器報錯與第 2 章修復

<a id="node-command-not-found"></a>
### `node: command not found`

**原因**：你執行的是依賴 Node.js 的額外程式。
**怎麼辦**：原生 Claude Code 不要求先裝 Node.js；若確實採用 npm 安裝，當前包要求 Node.js 22 或更高版本。若錯誤來自 MCP 伺服器，則查該伺服器的執行要求。

<a id="npm-warn-deprecated装的时候一堆警告"></a>
### `npm WARN deprecated`（裝的時候一堆警告）

**原因**：依賴庫版本提示，通常不影響功能。
**怎麼辦**：區分 warning（警告）和 error（失敗）；記錄警告所屬包，確認版本與維護狀態，不把所有黃色字一概忽略。

---

<a id="登录--认证"></a>
## 登入 / 認證

<a id="authentication-failed--401"></a>
### `Authentication failed` / 401

**原因**：token 過期 / 輸錯 / 沒許可權。
**怎麼辦**：
- `/logout` 然後 `/login` 重新登入
- 訂閱使用者確認計劃有效；API 或閘道器使用者核對實際提供方、憑據狀態與模型許可權，不用購買聊天訂閱解決 API 鑑權問題

<a id="unable-to-connect-to-apianthropiccom"></a>
### `Unable to connect to api.anthropic.com`

**原因**：網路問題（防火牆 / 代理 / 梯子）。
**怎麼辦**：
- 確認你能在瀏覽器訪問 https://anthropic.com
- 公司網路 → 問 IT 是否需要配代理
- 確認所在地區在服務支援範圍；訪問介紹網站成功不證明模型請求端點可用

---

<a id="使用阶段"></a>
## 使用階段

<a id="context-window-exceeded--上下文溢出"></a>
### `Context window exceeded` / 上下文溢位

**原因**：Ctx 爆了。
**怎麼辦**：
- 先保留任務目標、進展與待辦，再按任務是否連續選擇 `/compact` 或 `/clear`；後者不撤銷檔案
- 下次避免一次 @ 太多檔案

<a id="rate-limit-exceeded"></a>
### `Rate limit exceeded`

**原因**：短時間請求過多。
**怎麼辦**：
- 看錯誤說明和實際重置時間，使用 `/usage` 或服務控制檯查額度
- 區分短時間速率限制、訂閱使用視窗與 API 餘額
- 換模型不保證恢復所有額度，不要連續重試或輪換金鑰來碰運氣

<a id="claude-回答突然变笨--答非所问"></a>
### Claude 回答突然變笨 / 答非所問

**可能原因 A**：任務材料過多、目標混雜或關鍵條件未被保留；沒有通用的 80% 失效線
**辦法**：先儲存關鍵狀態，再整理材料；同一任務可 `/compact`，不相關新任務才 `/clear`

**可能原因 B**：模型換錯了（你上次切到 Haiku 忘了切回）
**辦法**：`/status` 看當前模型，`/model` 切回合適的

**可能原因 C**：prompt 太模糊
**辦法**：按 Ch 5 的 WHAT-WHERE-HOW-VERIFY 重構提示

<a id="claude-一直执行错误命令--循环中"></a>
### Claude 一直執行錯誤命令 / 迴圈中

**原因**：陷入區域性最優。
**怎麼辦**：
- 先中斷，檢查是否還有後臺任務在執行
- 核對已經執行的命令、檔案變化與外部影響
- 受跟蹤的編輯可用 `/rewind` 選擇恢復檔案；命令和外部副作用按實際狀態恢復
- 儲存狀態與待辦後，再決定繼續或 `/clear` 開新會話

---

<a id="权限--改文件"></a>
## 許可權 / 改檔案

<a id="permission-deniedclaude-想动某文件时"></a>
### `Permission denied`（Claude 想動某檔案時）

**原因**：系統級許可權不夠。
**怎麼辦**：
- 先核對目標路徑與當前使用者是否有權處理它；不要直接對整目錄執行 `chmod` / `chown`
- 系統保護目錄？→ **不要改**

<a id="diff-看着对但改完发现错了"></a>
### diff 看著對，但改完發現錯了

**可能原因**：差異檢查沒覆蓋實際行為、輸入有誤，或執行環境與預期不同。
**怎麼辦**：
- 開啟 `/rewind` 並確認該改動可恢復，再選恢復檔案
- 重新走，這次**細審**或 `/plan` 先

<a id="改完文件后发现多改了很多"></a>
### 改完檔案後發現多改了很多

**原因**：Claude "順手"多動
**怎麼辦**：
- 開啟 `/rewind` 核對恢復範圍；不在跟蹤範圍內的改動從備份或相應系統恢復
- 重講："只改 A，不動 B、C"

---

<a id="hooks--扩展"></a>
## Hooks / 擴充套件

<a id="hook-没触发"></a>
### Hook 沒觸發

**原因 A**：`settings.json` 格式錯
**辦法**：用本地編輯器或 `claude doctor` 檢查格式；含憑據的配置不要粘到線上校驗網站

**原因 B**：需要重啟
**辦法**：完全退出 Claude Code 重開

**原因 C**：matcher 匹配不上
**辦法**：核對事件、工具名和匹配規則，先在練習目錄測試限定的工具；不要把有副作用的 Hook 擴大到全部事件

<a id="hook-让-claude-code-卡住"></a>
### Hook 讓 Claude Code 卡住

**原因**：hook 命令慢 / 卡住。
**怎麼辦**：
- 按官方 Hook 配置設定超時；不要假定 Mac 自帶 GNU `timeout` 命令
- 先儲存配置副本，再移除相應 Hook 條目排查；JSON 不能隨意插入註釋

<a id="skill--command-没被识别"></a>
### Skill / Command 沒被識別

**原因 A**：檔案路徑錯
**辦法**：核對個人 `~/.claude/skills/<名>/SKILL.md`、專案 `.claude/skills/<名>/SKILL.md`，或相容舊格式 `.claude/commands/<名>.md`

**原因 B**：frontmatter 格式錯
**辦法**：若使用 frontmatter，檢查 `---` 開閉和 YAML 格式；舊命令也可以只有 Markdown，路徑與發現規則見第 20、21 章

**原因 C**：需要重啟
**辦法**：退出 Claude Code 重開

<a id="mcp-装了但-claude-说没有这个工具"></a>
### MCP 裝了但 Claude 說沒有這個工具

**原因 A**：配置作用域、地址或鑑權不對
**辦法**：在終端用 `claude mcp list` / `claude mcp get 名称` 核對，會話內用 `/mcp` 看連線與登入。專案共享配置為 `.mcp.json`；不要尋找舊稿寫錯的 `mcp_servers.json`。

**原因 B**：伺服器未啟動或缺少依賴
**辦法**：按該伺服器的官方說明檢查啟動命令與日誌。`server-xxx` 只是佔位名，不是該安裝的軟體包。

---

<a id="git-相关"></a>
## Git 相關

<a id="fatal-not-a-git-repository"></a>
### `fatal: not a git repository`

**原因**：當前目錄不是 git 專案。
**怎麼辦**：先確認是否進入了錯誤目錄。只有確實要為新專案啟用版本管理時才 `git init`，不要在任意位置初始化。

<a id="your-branch-is-ahead-of-originmain-by-n-commits"></a>
### `Your branch is ahead of 'origin/main' by N commits`

**原因**：本地比遠端新。
**怎麼辦**：這只是狀態提示，可以保持本地；只有確實要釋出並核對遠端、分支與待發提交時才按專案流程推送。

<a id="merge-conflict"></a>
### `Merge conflict`

**原因**：你和別人改了同檔案。
**怎麼辦**：
- **不要亂刪**——開啟衝突檔案看 `<<<<<<<` `=======` `>>>>>>>` 標記
- 理解雙方變更與共同目標，保留需要的內容
- 可讓 Claude 提合併方案和理由，稽核差異後執行相關檢查，不預設丟棄任意一邊

---

<a id="通用排查顺序"></a>
## 通用排查順序

遇到任何問題按這個順序試：

<!-- diagram: FIG-038 -->
![報錯時先收集這四樣](../../../assets/illustrations/FIG-038/revisions/r02/zh-CN.png)

*圖：保留操作、完整報錯、環境和已嘗試步驟，才更容易定位問題。*
<!-- /diagram: FIG-038 -->

1. **記錄錯誤、版本和觸發步驟**，儲存未完成工作
2. **`/status` 看配置，`/context` 看上下文，`/usage` 看用量**
3. **`/help` 看命令說明**
4. **看啟動時的日誌輸出**（有錯誤提示嗎？）
5. **搜關鍵詞**（GitHub issues / Reddit）
6. **問 Claude Code 自己**："我遇到 XXX 錯誤，怎麼辦？"（把建議當排查線索，執行前仍核對官方說明）

---

<a id="还是解决不了"></a>
## 還是解決不了？

- 官方 GitHub 開 issue 時提供脫敏錯誤、版本與系統；不公開金鑰、完整會話或私人路徑
- Reddit r/ClaudeAI 發帖
- 在普通終端用 `claude --version` 檢視版本；按原安裝方式更新

官方入口：[安裝與排錯](https://code.claude.com/docs/en/troubleshooting)、[命令表](https://code.claude.com/docs/en/commands)。

撤銷提示：本附錄提到 `/rewind` 時，都指開啟檢查點選單、確認恢復範圍；它不會逆轉任意命令、資料庫改動或外部操作。
