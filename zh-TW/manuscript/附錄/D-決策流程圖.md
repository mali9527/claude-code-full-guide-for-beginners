# 附錄 D：決策流程圖

> 本附錄把書裡反覆出現的幾個"該怎麼選"彙總成流程圖。圖全部用 Mermaid 手繪風格繪製，GitHub 上直接渲染，可以直接右鍵儲存圖片或截圖列印。

### 本章地圖（一眼看全貌）

<!-- diagram: MM-38 -->
```mermaid
---
config:
  theme: forest
  themeVariables:
    fontFamily: "-apple-system, 'SF Pro Text', 'PingFang SC', 'Helvetica Neue', sans-serif"
    fontSize: "17px"
    lineColor: "#D9D9D9"
---
mindmap
  root((附錄 D · 決策流程圖))
    圖 1 權限決策
      讀檔案一般 Yes
      改檔案先看 diff
      跑命令高危必退
    圖 2 模型選擇
      簡單用 Haiku
      日常用 Sonnet
      難題切 Opus
      超長切 Opus 1M
    圖 3 Ctx 應對
      50% 以下放心
      75% 就動手
      90% 斷崖
    圖 4 卡住怎麼辦
      5 分鐘原則
      不試第三次
      換方向或手動
    圖 5 資訊分層
      一次性會話說
      跨專案 MEMORY
      專案共享 CLAUDE
      流程化 Skill
    圖 6 擴充選型
      背景 CLAUDE.md
      流程 Skill
      快捷 Command
      重活 Subagent
      自動 Hook
      外網 MCP

```

## 圖 1：權限決策流程（遇到彈窗怎麼選）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["Claude 彈出權限視窗<br/>它要幹什麼?"] --> B{"操作型別"}
  B -->|"讀檔案"| C["通常 Yes<br/>除非是 .env、金鑰檔案"]
  B -->|"改檔案"| D{"先看 diff<br/>改的都是我想改的地方?"}
  B -->|"跑命令"| E{"是高危命令嗎?<br/>rm / force push / 刪表…"}
  D -->|"是"| F["Yes 接受"]
  D -->|"否"| G["No 退回讓它改"]
  E -->|"否"| H["Yes 接受"]
  E -->|"是"| I["詳細審一次再決定"]
```

**口訣**：

- 讀檔案 → 一般 Yes（除非是 `.env`、金鑰檔案）
- 改檔案 → **永遠看 diff**，多改了就 No
- 跑命令 → **高危必退**（詳見附錄 G）

## 圖 2：模型選擇流程（任務來了用哪個）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["新任務來了"] --> B{"需要深度推理嗎?"}
  B -->|"否：簡單查詢 / 翻譯 / 重新命名"| C["Haiku"]
  B -->|"是"| D{"上下文會超 200K 嗎?<br/>整本書 / 幾百個檔案"}
  D -->|"是"| E["Opus 1M"]
  D -->|"否"| F{"日常活還是硬核活?"}
  F -->|"日常（80% 場景）"| G["Sonnet（預設）"]
  F -->|"複雜推理 / 卡住了"| H["Opus"]
```

**新手一句話**：**預設 Sonnet，卡住切 Opus，簡單事用 Haiku**。

## 圖 3：Ctx% 使用率應對流程

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["瞥一眼狀態列<br/>看 Ctx 百分比"] --> B{"落在哪個區間?"}
  B -->|"0 - 50%"| C["繼續寫，無需操心"]
  B -->|"50 - 75%"| D["準備整理<br/>快完就收尾<br/>還長就 /compact"]
  B -->|"75 - 90%"| E["立刻 /compact 或 /clear"]
  B -->|"超過 90%"| F["斷崖區<br/>馬上 /clear 或退出重啟"]
```

**口訣**：**看到 75% 就動手，別等 90%**。

## 圖 4：卡住了怎麼辦（5 分鐘原則）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["第 1 次嘗試失敗"] --> B["調整 prompt 再試一次"]
  B --> C{"第 2 次還是不行?"}
  C -->|"是"| D["觸發 5 分鐘原則<br/>先估算手動要多久"]
  D --> E{"手動完成大概需要?"}
  E -->|"5 分鐘以內"| F["關掉 Claude<br/>自己動手做完"]
  E -->|"20 分鐘以上"| G["繼續用 AI，換方向:<br/>/rewind 重開<br/>/compact 清包袱<br/>換模型 / 拆小任務"]
  E -->|"5 - 20 分鐘"| H["任選：自己做 或 換方向"]
```

**口訣**：**同一個 prompt 不要試第三次**。

## 圖 5：資訊分層決策（該放在哪一層）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["這條資訊…"] --> B{"是什麼性質?"}
  B -->|"一次性用的"| C["會話裡說就行<br/>不用存"]
  B -->|"跨專案 + 關於我的"| D["MEMORY.md"]
  B -->|"專案規則 + 團隊共享"| E["CLAUDE.md"]
  B -->|"結構化任務流程（偶爾用）"| F["Skill"]
  B -->|"外部已有長文件"| G["在 CLAUDE.md 寫 Pointer<br/>（詳見 XXX）"]
```

**口訣**：**越私人越往 MEMORY，越團隊越往 CLAUDE，越流程化越往 Skill**。

## 圖 6：擴充機制選型

<!-- diagram: MM-01 -->
```mermaid
---
config:
  theme: forest
  themeVariables:
    fontFamily: "-apple-system, 'SF Pro Text', 'PingFang SC', 'Helvetica Neue', sans-serif"
    fontSize: "17px"
    lineColor: "#D9D9D9"
---
mindmap
  root((我想讓 Claude...))
    知道專案背景
      CLAUDE.md
    會做某類任務
      Skill
    敲 /xxx 一鍵觸發
      Custom Command
    派獨立專員乾重活
      Subagent
    某事件自動觸發
      Hook
    連線外部系統
      MCP
```

**口訣**：**CLAUDE.md 講背景，Skill 講流程，Command 給快捷鍵，Subagent 派替身，Hook 搞自動，MCP 接外網**。


---

<!-- chapter-nav -->

📖  [← 附錄 C · Slash 命令全表](C-Slash命令全表.md)  ·  [📑 返回目錄](../../README.md)  ·  [附錄 E · FAQ 10 問 →](E-FAQ.md)
