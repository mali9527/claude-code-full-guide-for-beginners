<a id="附录-d决策流程图"></a>
# 附錄 D：決策流程圖

> 本附錄把書裡反覆出現的幾個"該怎麼選"彙總成流程圖。圖全部用 Mermaid 手繪風格繪製，GitHub 上直接渲染，可以直接右鍵儲存圖片或截圖列印。

<a id="本章地图一眼看全貌"></a>
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
  root((附录 D · 决策流程图))
    图 1 权限决策
      读取先确认材料范围
      改文件先看 diff
      命令先看作用与范围
    图 2 模型选择
      简单用 Haiku
      日常先用 Opus 5.5
      难题再评估 Fable
      查实际上下文
    图 3 Ctx 应对
      先看任务是否清楚
      长任务及时整理
      换任务开新会话
    图 4 卡住怎么办
      5 分钟原则
      不试第三次
      换方向或手动
    图 5 信息分层
      一次性会话说
      个人规则用用户说明
      项目共享 CLAUDE
      流程化 Skill
    图 6 扩展选型
      背景 CLAUDE.md
      流程 Skill
      快捷 Command
      重活 Subagent
      自动 Hook
      外部工具与数据 MCP

```

<a id="图-1权限决策流程遇到弹窗怎么选"></a>
## 圖 1：許可權決策流程（遇到彈窗怎麼選）

<!-- diagram: FC-legacy-01 -->
```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["Claude 弹出权限窗口<br/>它要干什么?"] --> B{"操作类型"}
  B -->|"读文件"| C["核对任务授权与内容敏感性<br/>未知先暂停"]
  B -->|"改文件"| D{"先看 diff<br/>改的都是我想改的地方?"}
  B -->|"跑命令"| E{"已理解路径和影响吗?<br/>删除 / 外发 / 发布等"}
  D -->|"是"| F["Yes 接受"]
  D -->|"否"| G["No 退回让它改"]
  E -->|"否"| H["先让它解释，不批准"]
  E -->|"是"| I["核对任务范围后再决定"]
```

**口訣**：

- 讀檔案 → 確認屬於本次任務材料，且內容適合交給所連線的服務
- 改檔案 → **永遠看 diff**，多改了就 No
- 跑命令 → 先理解路徑、作用範圍與外部影響，不因“沒在黑名單”就批准
- 這張圖用於出現詢問時；預先允許或自動執行的結果也要檢查

<a id="图-2模型选择先看任务结果与预算"></a>
## 圖 2：模型選擇，先看任務結果與預算

| 現在遇到什麼 | 下一步 |
|---|---|
| 剛開始一個日常任務 | 從賬戶提供的 Opus 5.5 等日常模型開始 |
| 結果不對 | 先檢查材料、目標、驗證標準，必要時調整 effort |
| 已說明清楚，任務仍很複雜 | 核對 Fable 5.1 的訪問資格和費用，再比較實際效果 |
| 更在意響應速度或成本 | 在可用模型中比較 Sonnet / Haiku，不假定低價必然夠用 |
| 材料很長 | 用 `/context` 看實際使用情況，整理材料；不要只根據宣傳視窗大小做決定 |

詳細定價和切換行為見第 15 章。`/fast` 是單獨的速度與費用選項，不等於換成小模型。

<a id="图-3上下文管理先问还在做同一件事吗"></a>
## 圖 3：上下文管理，先問“還在做同一件事嗎”

| 當前情況 | 處理方式 |
|---|---|
| 任務清楚、材料夠用、結果正確 | 繼續，不必為了某個百分比打斷工作 |
| 同一長任務需要減輕上下文 | 先儲存目標、進展和待辦，再用 `/compact` 整理 |
| 要開始不相關的新任務 | 儲存成果後用 `/clear` 開新對話 |
| 已出現遺漏或自相矛盾 | 先核對來源和關鍵條件，必要時重新提供任務摘要 |

沒有“90% 一定變笨”的統一規則。自動壓縮時點也會受模型與配置影響；第 12 章解釋這些差別。

<a id="图-4卡住了怎么办5-分钟原则"></a>
## 圖 4：卡住了怎麼辦（5 分鐘原則）

<!-- diagram: FC-legacy-02 -->
```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["第 1 次尝试失败"] --> B["调整 prompt 再试一次"]
  B --> C{"第 2 次还是不行?"}
  C -->|"是"| D["触发 5 分钟原则<br/>先估算手动要多久"]
  D --> E{"手动完成大概需要?"}
  E -->|"5 分钟以内"| F["关掉 Claude<br/>自己动手做完"]
  E -->|"20 分钟以上"| G["继续用 AI，换方向:<br/>/rewind 重开<br/>/compact 清包袱<br/>换模型 / 拆小任务"]
  E -->|"5 - 20 分钟"| H["任选：自己做 或 换方向"]
```

這裡的兩次嘗試與五分鐘是作者的時間管理建議，不是產品限制。若失敗涉及外部副作用，先核對現狀再決定恢復方式。

<a id="图-5信息分层决策该放在哪一层"></a>
## 圖 5：資訊分層決策（該放在哪一層）

<!-- diagram: FC-legacy-03 -->
```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["这条信息…"] --> B{"是什么性质?"}
  B -->|"一次性用的"| C["会话里说就行<br/>不用存"]
  B -->|"跨项目个人规则"| D["用户 CLAUDE.md"]
  B -->|"项目规则 + 团队共享"| E["CLAUDE.md"]
  B -->|"结构化任务流程（偶尔用）"| F["Skill"]
  B -->|"外部已有长文档"| G["在 CLAUDE.md 写 Pointer<br/>（查看项目中实际存在的说明文件）"]
```

專案自動記憶預設按專案儲存，不是天然的跨專案偏好庫。個人規則與團隊共享規則分開維護，任務流程放進 Skill。

<a id="图-6扩展机制选型"></a>
## 圖 6：擴充套件機制選型

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
  root((我想让 Claude...))
    知道项目背景
      CLAUDE.md
    会做某类任务
      Skill
    敲 /xxx 一键触发
      手动调用 Skill
    派独立专员干重活
      Subagent
    某事件自动触发
      Hook
    连接外部系统
      MCP
```

**口訣**：**CLAUDE.md 講背景，Skill 講流程，Slash 呼叫 Skill，Subagent 派替身，Hook 搞自動，MCP 連線外部工具和資料來源**。
