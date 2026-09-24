<a id="附录-i延伸阅读与来源致谢"></a>
# 附錄 I：延伸閱讀與來源致謝

> **核驗日期：2026-09-24。**遇到版本、命令、模型或費用差異，先看官方當期說明，再結合自己賬戶與安裝版本驗證。社群教程用於學習和查漏。

<a id="本章地图一眼看全貌"></a>
### 本章地圖（一眼看全貌）

本附錄按下方問題和條目查閱；相關章節入口保留在各條目中。

<a id="一最先收藏的官方入口"></a>
## 一、最先收藏的官方入口

| 你現在要查什麼 | 從這裡進入 | 怎樣使用 |
|---|---|---|
| 安裝、日常命令和各功能的現行規則 | [Claude Code 官方文件](https://code.claude.com/docs/en/overview) | 搜具體功能名；注意適用版本和環境 |
| 某個版本改了什麼 | [官方 CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) | 對照本機版本，區分已釋出變化和自己的賬戶是否開放 |
| 產品問題與已知故障 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | 檢視相關問題；不要把單條 Issue 當成所有使用者都必現 |
| 新模型正式釋出及能力說明 | [Anthropic 產品訊息](https://www.anthropic.com/news) | 模型名稱、釋出日期與接入資格分別核對 |
| Skills 怎樣寫與怎樣載入 | [技能文件](https://code.claude.com/docs/en/skills)、[官方示例倉庫](https://github.com/anthropics/skills) | 看當前格式，先在練習專案試一個 |
| 桌面、遠端、定時任務 | [Desktop](https://code.claude.com/docs/en/desktop)、[Remote Control](https://code.claude.com/docs/en/remote-control)、[雲端 Routines](https://code.claude.com/docs/en/routines) | 先確認任務在哪裡執行，再看條件與許可權 |

本書仍以零基礎操作和理解為主，官方文件是按功能查詢的資料庫。你不用從頭把它讀完：遇到“介面裡為什麼沒有這個選項”，先看相關頁面的適用條件，往往比重複安裝更有用。

<a id="二找回本书早期参考的那份-github-教程"></a>
## 二、找回本書早期參考的那份 GitHub 教程

作者是 **Florian Bruniaux**，倉庫是 [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)。它仍可公開訪問，是本書早期組織學習主題與延伸閱讀的參考之一。

本專案早期需求記錄提到了源指南 **v3.39.1**，也曾將“信任校準”“新手錯誤”等主題與其相關章節對應。本次檢查可見的[命令速查頁](https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/guide/cheatsheet.md)標註 **3.43.0 / 2026-08-30**。這是該頁面的標註，**不等於我們已經確認整個倉庫截至今天的最新版本**；網頁快取與不同檔案的更新時間可能不同。

這份教程面向較有經驗的使用者，適合用來發現還有哪些專題值得研究。建議先在其目錄、[變更記錄](https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/CHANGELOG.md)裡找到問題，再回到對應官方文件核實。長教程也會有區域性滯後，尤其是模型、價格、許可權、命令名稱，不能因為倉庫最近提交過，就預設每一張表都已經同步。

本輪修訂保留本書面向普通人的解釋、操作練習和判斷方式；以參考教程查漏，以官方來源核對事實，重新編寫中文說明與案例，並不逐章翻譯上游正文。感謝 Florian Bruniaux 持續整理相關資料。上游採用 [CC BY-SA 4.0](https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/LICENSE)；本書自己的許可見 [LICENSE](../../../LICENSE)。引用和來源致謝不改變各作品的許可，不能把上游材料直接套用成本書的許可。

<a id="三另一份明确影响过本书的文章"></a>
## 三、另一份明確影響過本書的文章

HumanLayer 的 [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)，作者署名 Kyle，發表於 2025-11-25，是第 14 章早期討論簡短規則、專案說明與按需提供材料的參考來源。

它屬於作者實踐文章，讀它時要區分“有價值的經驗”和“產品硬性規定”。例如有關檔案長度、自動生成規則的建議，需要結合你的專案驗證，不能直接寫成 Claude Code 永久不變的限制。使用 `/init` 得到初稿之後認真刪改，與不經檢查就長期保留生成內容，是兩種不同做法。

你可以拿自己的專案做一次比較：保留真正通用的要求，把僅對特定任務有用的材料移到單獨檔案或技能，再用同一項真實任務觀察差異。這樣讀完文章得到的是經過檢驗的工作習慣，而不是又多了幾句必須死記的口號。

<a id="四按实际需要继续深入"></a>
## 四、按實際需要繼續深入

| 當前目標 | 資料 | 不必急著做的事 |
|---|---|---|
| 讓一類輸出更穩定 | [Claude 平臺文件](https://platform.claude.com/docs/en/home)中的提示與評估資料 | 不必為了使用新名詞重寫整套流程 |
| 把 Claude 整合進自己的程式 | [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) | 先區分它與普通互動式 Claude Code 的執行和計費方式 |
| 接入一個外部服務 | [MCP 官方入門](https://modelcontextprotocol.io/docs/getting-started/intro)和該服務商文件 | 不必一次安裝許多不使用的連線 |
| 看可執行的程式示例 | [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) | 先讀依賴和說明，再在自己的練習環境執行 |
| 補 Git 基礎 | [Pro Git 中文版](https://git-scm.com/book/zh/v2) | 先理解儲存、差異、分支，再學複雜協作 |
| 補 Markdown | [Markdown 語法速查](https://www.markdownguide.org/cheat-sheet/) | 先用標題、列表和連結表達清楚 |

社群討論、影片和個人文章適合發現使用場景。引用其中的建議前，問三個問題：它針對哪個版本與環境，作者是否展示了可檢查的結果，換成我的材料是否仍成立。資料舊不代表思想全錯，資料新也不代表每條事實都可靠。

<a id="五一个可持续的学习节奏"></a>
## 五、一個可持續的學習節奏

先連續做幾次你真實需要的任務：整理筆記、修改文件、檢查小專案。記下反覆出現的困難，再選一章或一個官方頁面深入。完成一個練習之後，留下輸入材料、成功標準和你確實觀察到的結果；下一次版本更新，拿同一個小例子複驗。

每隔一段時間檢查當前用到的功能就夠了。發現新模型時，先看賬戶能否使用，再拿熟悉的任務比較；發現新的自動化入口時，先確認執行地點、停止方式和費用。不要把追完所有更新當作學習完成的標準。

> 本書作者：**馬力** · [@mali9527](https://github.com/mali9527)
> 本書原創內容的使用條件見 [LICENSE](../../../LICENSE)；所連結的外部資料保留各自作者與許可。
