<div align="center">

<img src="../assets/cover.png" alt="Claude Code 零基礎入門指南" width="820" />

# Claude Code 零基礎入門指南

**一本寫給完全零基礎讀者的 Claude Code 系統入門書** · **針對 Claude Opus 4.7 全面更新**
不會程式設計、沒用過終端、沒碰過 AI 程式設計工具，也能從零讀到上手用。

📖 從**終端 / 命令列**入門講起，覆蓋 **安裝配置 · 讀檔案 / 改檔案 / 跑命令 · 權限機制 · 互動迴圈七步法 · 計劃模式與撤銷 · 信任校準 · 資料隱私 · 三層記憶 · CLAUDE.md · 模型與成本（Opus 4.7 / Sonnet / Haiku 選型） · Prompt 輸入技巧 · Skills / 自定義 Slash 命令 / Subagents / Hooks / MCP 五大擴充 · 團隊協作**，全程 **Mac / Windows 雙平臺**手把手，配 **44 張 Mermaid 思維導圖**。專設 **附錄 J** 集中講 Opus 4.7 的新概念、effort 檔位、分詞器變化與新手坑。

<sub>🏷️ **關鍵詞**：Claude Code 中文教程 · Claude Code 入門 · Claude Opus 4.7 · Opus 4.7 新手指南 · Opus 4.7 使用教程 · Claude Opus 4.7 中文 · effort xhigh · Anthropic · AI 程式設計 · AI 程式設計助手 · AI Coding · 智慧程式設計 · 零基礎 · 新手入門 · 命令列入門 · 終端教程 · Prompt 工程 · 提示詞技巧 · Agentic AI · Subagents · MCP · Hooks · Skills · Mac 教程 · Windows 教程 · Claude Code tutorial · Claude Opus 4.7 guide · Claude Code Chinese guide · beginner-friendly · zero-to-hero · learn AI coding</sub>

[![Stars](https://img.shields.io/github/stars/mali9527/claude-code-full-guide-for-beginners?style=flat-square&color=5C9F5C&label=⭐%20Stars)](../../stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/mali9527/claude-code-full-guide-for-beginners?style=flat-square&color=5C9F5C&label=最近更新)](../修订日志.md)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-D5A021?style=flat-square)](../LICENSE)
![Language](https://img.shields.io/badge/語言-繁體中文-D5A021?style=flat-square)
![Status](https://img.shields.io/badge/狀態-持續更新中-brightgreen?style=flat-square)
![Word Count](https://img.shields.io/badge/字數-17萬+-5C9F5C?style=flat-square)
![Chapters](https://img.shields.io/badge/章節-27章+10附錄-5C9F5C?style=flat-square)
![Opus 4.7](https://img.shields.io/badge/針對-Claude%20Opus%204.7-D5A021?style=flat-square)

### [📖 一口氣讀完全書](./全書.md) &nbsp;·&nbsp; [📚 按章節讀](#-完整目錄) &nbsp;·&nbsp; ⭐ **[點個 Star](../../stargazers) 支援本書持續更新**

</div>

---

> 🌐 **語言**： [简体中文](../README.md) · **繁體中文（本頁）** · English（coming soon）

## 你是不是也遇到過這些

- 聽說 **Claude Code 很強**，開啟教程一看全是"開啟終端"、"pip install"、"cd 目錄"——**直接勸退**
- 裝上了但**不敢讓它改檔案**，怕它把整個專案搞壞
- 用了兩三次就覺得它**"變糊塗"**了，不知道為什麼，也不知道怎麼辦
- 想深入用，但 **Skill / Subagent / MCP / Hook** 這一堆詞看起來像天書
- 每次有問題都得去翻英文文件 / Discord，**中文資料**要麼太舊要麼太淺

**這本書就是寫給這樣的你的。**

我們假設你**完全零基礎**——不會程式設計、沒用過終端、沒裝過 AI 程式設計工具——然後**手把手**帶你走完 27 章 + 10 份附錄，從"把電腦準備好"開始，到最後能把 Claude Code **穩定用在自己的日常工作裡**。

---

## ✨ 讀完你會學會什麼

不是"看完有個印象"，而是**真的能上手做**：

1. ✅ **正確安裝與配置** Claude Code（Mac / Windows 雙平臺每一步都手把手）
2. ✅ 看懂 Claude Code **到底是什麼**（而不是"就當它是黑盒子用"）
3. ✅ 熟練讓它**讀檔案、改檔案、跑命令**——以及如何**穩妥地授權**
4. ✅ 理解它為什麼會"**變糊塗**"，並在糊塗之前就察覺訊號
5. ✅ 掌握**三層記憶機制**（會話 / MEMORY / CLAUDE.md），讓它越用越懂你
6. ✅ 用好**計劃模式、撤銷、信任校準**——繞開新手最常踩的 10 大坑
7. ✅ 按需上手 **Skills / Slash 命令 / Subagents / Hooks / MCP** 5 大擴充能力
8. ✅ 懂得**什麼時候該停下來**，什麼時候該讓它繼續
9. ✅ 寫出人話版 prompt——而不是抄模板、背咒語
10. ✅ 讀懂錯誤資訊 + 學會自救——知道**什麼時候該重開一局**

---

## 🎯 本書獨特之處

|  |  |
|---|---|
| 🎓 **真正的零基礎** | 不假設你會程式設計，不假設你用過終端。**從"怎麼開啟終端"開始講** |
| 🖥️ **Mac / Windows 雙平臺全覆蓋** | 每一步操作都給兩套命令，**不讓 Windows 使用者靠猜** |
| 🗺️ **43 張思維導圖** | 每章開頭一張"章首導覽"——**一眼看清全章結構**；重要概念另配專題導圖 |
| ✍️ **動手任務驅動** | 每章末尾"動手做一做"——**不是讓你抄一遍，而是讓你真的在自己電腦上跑起來** |
| 🆓 **完全免費開源** | 全本書稿 + 插圖原始碼都在這個倉庫裡，**歡迎 Fork、翻譯、改編** |
| 🔄 **持續跟版更新** | 跟隨 Claude Code 官方版本迭代同步修訂，每次變更記錄在 [修訂日誌](../修订日志.md) |

---

## 📚 這本書適合你嗎？

| 你的情況 | 這本書 |
|---|---|
| 聽過 AI 程式設計，但沒實際用過 | ✅ 正合適 |
| 沒寫過程式碼 / 只會一點點 | ✅ 正合適 |
| 對 Mac / Windows 終端有模糊印象但不太敢用 | ✅ 正合適 |
| 想讓 AI 幫你處理日常工作（非純程式設計） | ✅ 正合適 |
| 已經熟練使用 Claude Code / Cursor / Copilot | ❌ 這本太基礎了 |
| 想學純程式設計入門（Python / JavaScript） | ❌ 這不是程式設計書 |

---

## 🚀 怎麼開始讀

有兩種方式，挑一種順手的：

<table>
<tr>
<td width="50%" valign="top">

### 📖 [一口氣讀完（全書合訂版）](./全書.md)

所有章節拼在一個頁面裡，**從上滾到底就讀完了**。

**適合**：想沉浸式從頭讀到尾、或在手機 / 平板上連續閱讀。

</td>
<td width="50%" valign="top">

### 📚 [按章節讀（見下方目錄）](#-完整目錄)

每章一個獨立 URL，**方便收藏、分享單章、跳著讀**。

**適合**：按章節做動手任務、或日後回來查某一章。

</td>
</tr>
</table>

> 💡 **建議**：首次通讀**從第 0 章開始**順著讀，每章做完"動手任務"再進下一章。別跳章——前 5 章顆粒度最細，是整本書的地基。

---

## 🔥 不知道從哪開始？試試這 3 章

如果你想先"試讀"感受一下本書風格，我們建議從這三章開始：

- 🌱 **[第 3 章 · 你的第一次對話](./manuscript/part1-從零起步/03-你的第一次對話.md)** — 手把手帶你和 Claude Code 說第一句話，**每一步都有預期結果 + 失敗兜底**
- 🧠 **[第 13 章 · 三層記憶](./manuscript/part3-深度概念/13-三層記憶.md)** — 理解 Claude "記性"的真相，**配 mindmap 一眼看穿**
- ⚠️ **[第 16 章 · 新手 10 大錯誤](./manuscript/part4-避坑與判斷力/16-新手10大錯誤.md)** — 把別人踩過的坑一次看完，**省你半年學習成本**

---

## 📖 完整目錄

### 前言
- [00 本書怎麼讀](./manuscript/00-前言/00-本書怎麼讀.md)

### 第一部分 · 從零起步
> 前 5 章是全書顆粒度最細的地方，每一步都有 Mac / Windows 分開的完整流程和失敗兜底。

- [01 先把電腦準備好](./manuscript/part1-從零起步/01-先把電腦準備好.md)
- [02 安裝 Claude Code](./manuscript/part1-從零起步/02-安裝-Claude-Code.md)
- [03 你的第一次對話](./manuscript/part1-從零起步/03-你的第一次對話.md)
- [04 Claude Code 到底是什麼](./manuscript/part1-從零起步/04-Claude-Code到底是什麼.md)

### 第二部分 · 日常使用
> 掌握"讀檔案 / 改檔案 / 跑命令"三件核心互動，加上權限機制、互動迴圈七步法、計劃模式、撤銷、信任校準——你就能安心用它處理日常任務了。

- [05 讓它讀檔案](./manuscript/part2-日常使用/05-讓它讀檔案.md)
- [06 讓它改檔案](./manuscript/part2-日常使用/06-讓它改檔案.md)
- [07 讓它跑命令加權限機制](./manuscript/part2-日常使用/07-讓它跑命令加權限機制.md)
- [08 互動迴圈七步法](./manuscript/part2-日常使用/08-互動迴圈七步法.md)
- [09 計劃模式與撤銷](./manuscript/part2-日常使用/09-計劃模式與撤銷.md)
- [10 信任校準](./manuscript/part2-日常使用/10-信任校準.md)

### 第三部分 · 深度概念
> 為什麼 Claude 會變糊塗？記憶分幾層？CLAUDE.md 怎麼寫才有效？這一部分講清楚"為什麼"。

- [11 你的資料去哪了](./manuscript/part3-深度概念/11-你的資料去哪了.md)
- [12 Claude 為什麼會變糊塗](./manuscript/part3-深度概念/12-Claude為什麼會變糊塗.md)
- [13 三層記憶](./manuscript/part3-深度概念/13-三層記憶.md)
- [14 寫好你的 CLAUDE.md](./manuscript/part3-深度概念/14-寫好你的CLAUDE.md.md)
- [15 模型與成本](./manuscript/part3-深度概念/15-模型與成本.md)

### 第四部分 · 避坑與判斷力
> 新手最容易踩的 10 個坑、什麼時候該停下來別讓 AI 繼續、怎麼用好 Slash 命令和 prompt 技巧。

- [16 新手 10 大錯誤](./manuscript/part4-避坑與判斷力/16-新手10大錯誤.md)
- [17 什麼時候該停下來](./manuscript/part4-避坑與判斷力/17-什麼時候該停下來.md)
- [18 常用快捷命令全覽](./manuscript/part4-避坑與判斷力/18-常用快捷命令全覽.md)
- [19 輸入技巧](./manuscript/part4-避坑與判斷力/19-輸入技巧.md)

### 第五部分 · 擴充能力
> 當預設功能不夠用：用 Skill 打包重複任務、用 Command 做快捷指令、用 Subagent 派替身、用 Hook 自動觸發、用 MCP 接外部系統。

- [20 Skills 入門](./manuscript/part5-擴充能力/20-Skills入門.md)
- [21 自定義 Slash 命令](./manuscript/part5-擴充能力/21-自定義Slash命令.md)
- [22 Subagents 入門](./manuscript/part5-擴充能力/22-Subagents入門.md)
- [23 Hooks 入門](./manuscript/part5-擴充能力/23-Hooks入門.md)
- [24 MCP 入門](./manuscript/part5-擴充能力/24-MCP入門.md)

### 第六部分 · 融入日常
> 從"能用"到"用熟"：團隊協作、進階能力速覽、下一步路線。

- [25 團隊協作基礎](./manuscript/part6-融入日常/25-團隊協作基礎.md)
- [26 進階能力速覽](./manuscript/part6-融入日常/26-進階能力速覽.md)
- [27 下一步路線](./manuscript/part6-融入日常/27-下一步路線.md)

### 附錄（按需查閱）
- [A Mac 終端速查](./manuscript/附錄/A-Mac終端速查.md) · 命令 + 快捷鍵 + 常見錯誤
- [B Windows PowerShell 速查](./manuscript/附錄/B-Windows-PowerShell速查.md)
- [C Slash 命令全表](./manuscript/附錄/C-Slash命令全表.md) · 按用途分組 + 組合套路
- [D 決策流程圖](./manuscript/附錄/D-決策流程圖.md) · 權限 / 模型 / Ctx / 卡住 / 資訊分層 / 擴充選型
- [E FAQ](./manuscript/附錄/E-FAQ.md) · 10 個最高頻問題
- [F 術語表](./manuscript/附錄/F-術語表.md) · 40+ 英文詞 + 本書概念
- [G 報錯自救手冊](./manuscript/附錄/G-報錯自救手冊.md) · 分階段速查
- [H 桌面應用導覽](./manuscript/附錄/H-桌面應用導覽.md) · 終端 ↔ 桌面概念對照
- [I 延伸閱讀](./manuscript/附錄/I-延伸閱讀.md) · 六級資源 + 90 天學習節奏
- [J Claude Opus 4.7 新手指南](./manuscript/附錄/J-Opus-4.7新手指南.md) · **2026-04 新增** · 新特性 + effort 檔位 + 分詞器變化 + 5 大新手坑

---

## 💬 反饋 & 參與

讀到覺得哪裡不清楚、哪裡有錯、哪裡可以寫得更好——**歡迎告訴我**：

- 🐛 **發現錯誤 / 提出建議**：[提一個 Issue](../../issues/new)
- 💡 **貢獻改進**：Fork 本倉庫 → 改完 → 提 PR
- ⭐ **覺得這本書有用**：[點個 Star](../../stargazers)——每個 Star 都是我繼續更新的動力
- 👀 **想第一時間看到更新**：點右上角 **Watch → Custom → Releases** 就行

> 這本書會**持續跟隨 Claude Code 官方版本迭代同步修訂**。如果你 Star 了，每次大版本更新你都能第一時間看到。

---

## 📊 專案狀態

- **2026-04-19** · 正文全書首版成稿（27 章 + 9 附錄 ≈ 17 萬字）
- **2026-04-20** · 引入 Mermaid mindmap 插圖機制，全書加入 43 張思維導圖
- **2026-04-20** · 新增全書單頁合訂版 + 每章上下篇導航
- **2026-04-21** · **新增附錄 J：Claude Opus 4.7 新手指南**（配套 Anthropic 2026-04-16 釋出的 Opus 4.7）
- 詳細版本記錄見 [修訂日誌.md](../修订日志.md)

---

## 📝 關於這本書

- **作者**：馬力（[@mali9527](https://github.com/mali9527)）
- **開源許可**：[CC BY-NC-SA 4.0](../LICENSE)——允許自由傳播 / 修改 / 翻譯，**禁止商用**，修改後必須保持同樣協議開源。
- **多語言版本**：這是 **繁體中文版**；原版 [簡體中文版](../README.md) 也在同倉庫。歡迎翻譯成其他語言（詳見 [LICENSE](../LICENSE) 裡的翻譯說明）。
- **引用本書**：歡迎引用 / 轉載 / 用於公開課素材，請保留原始倉庫連結即可。
- **想參與寫作 / 改稿**：讀 [CONTRIBUTING.md](../CONTRIBUTING.md)，從改一個錯字到貢獻整章都歡迎。

---

<details>
<summary><b>🛠  如果你是來參與寫作 / 改稿的</b></summary>

本書是一個正在演化的書稿專案。參與寫作前請先讀：

- [需求文件.md](../需求文档.md) — **權威規格**，所有寫作決策的源頭。尤其是 §1-3（背景、讀者畫像、學習目標）和 §6（兩條鐵律）
- [寫作規範.md](../写作规范.md) — 每日寫作的 quick reference
- [術語翻譯表.md](../术语翻译表.md) — 術語→生活化翻譯的唯一真源
- [templates/章節模板.md](../templates/章节模板.md) — 新寫章節的起始模板
- [assets/diagrams/README.md](../assets/diagrams/README.md) — 插圖管理清單與規範
- [CLAUDE.md](../CLAUDE.md) — 協作硬規則（給 Claude Code 會話看）

寫完新章節後：

1. 用術語翻譯表掃一遍一致性
2. 更新 [修訂日誌.md](../修订日志.md)
3. 如果涉及插圖，去 `assets/diagrams/README.md` 登記
4. 重跑 `/tmp/build_book.py` 同步 `全書.md` 和章末導航

</details>

<div align="center">

---

**如果這本書對你有幫助，[給個 ⭐ Star](../../stargazers) 就是最好的鼓勵。**

</div>
