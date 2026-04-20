# 附录 D：决策流程图

> 本附录把书里反复出现的几个"该怎么选"汇总成流程图。图全部用 Mermaid 手绘风格绘制，GitHub 上直接渲染，可以直接右键保存图片或截图打印。

### 本章地图（一眼看全貌）

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
      读文件一般 Yes
      改文件先看 diff
      跑命令高危必退
    图 2 模型选择
      简单用 Haiku
      日常用 Sonnet
      难题切 Opus
      超长切 Opus 1M
    图 3 Ctx 应对
      50% 以下放心
      75% 就动手
      90% 断崖
    图 4 卡住怎么办
      5 分钟原则
      不试第三次
      换方向或手动
    图 5 信息分层
      一次性会话说
      跨项目 MEMORY
      项目共享 CLAUDE
      流程化 Skill
    图 6 扩展选型
      背景 CLAUDE.md
      流程 Skill
      快捷 Command
      重活 Subagent
      自动 Hook
      外网 MCP

```

## 图 1：权限决策流程（遇到弹窗怎么选）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["Claude 弹出权限窗口<br/>它要干什么?"] --> B{"操作类型"}
  B -->|"读文件"| C["通常 Yes<br/>除非是 .env、密钥文件"]
  B -->|"改文件"| D{"先看 diff<br/>改的都是我想改的地方?"}
  B -->|"跑命令"| E{"是高危命令吗?<br/>rm / force push / 删表…"}
  D -->|"是"| F["Yes 接受"]
  D -->|"否"| G["No 退回让它改"]
  E -->|"否"| H["Yes 接受"]
  E -->|"是"| I["详细审一次再决定"]
```

**口诀**：

- 读文件 → 一般 Yes（除非是 `.env`、密钥文件）
- 改文件 → **永远看 diff**，多改了就 No
- 跑命令 → **高危必退**（详见附录 G）

## 图 2：模型选择流程（任务来了用哪个）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["新任务来了"] --> B{"需要深度推理吗?"}
  B -->|"否：简单查询 / 翻译 / 重命名"| C["Haiku"]
  B -->|"是"| D{"上下文会超 200K 吗?<br/>整本书 / 几百个文件"}
  D -->|"是"| E["Opus 1M"]
  D -->|"否"| F{"日常活还是硬核活?"}
  F -->|"日常（80% 场景）"| G["Sonnet（默认）"]
  F -->|"复杂推理 / 卡住了"| H["Opus"]
```

**新手一句话**：**默认 Sonnet，卡住切 Opus，简单事用 Haiku**。

## 图 3：Ctx% 使用率应对流程

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["瞥一眼状态栏<br/>看 Ctx 百分比"] --> B{"落在哪个区间?"}
  B -->|"0 - 50%"| C["继续写，无需操心"]
  B -->|"50 - 75%"| D["准备整理<br/>快完就收尾<br/>还长就 /compact"]
  B -->|"75 - 90%"| E["立刻 /compact 或 /clear"]
  B -->|"超过 90%"| F["断崖区<br/>马上 /clear 或退出重启"]
```

**口诀**：**看到 75% 就动手，别等 90%**。

## 图 4：卡住了怎么办（5 分钟原则）

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

**口诀**：**同一个 prompt 不要试第三次**。

## 图 5：信息分层决策（该放在哪一层）

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral", "themeVariables": {"fontFamily": "'Chalkboard SE','Comic Sans MS','Segoe Print','Kaiti SC','STKaiti','KaiTi','Bradley Hand',cursive", "fontSize": "15px"}}}%%
flowchart TD
  A["这条信息…"] --> B{"是什么性质?"}
  B -->|"一次性用的"| C["会话里说就行<br/>不用存"]
  B -->|"跨项目 + 关于我的"| D["MEMORY.md"]
  B -->|"项目规则 + 团队共享"| E["CLAUDE.md"]
  B -->|"结构化任务流程（偶尔用）"| F["Skill"]
  B -->|"外部已有长文档"| G["在 CLAUDE.md 写 Pointer<br/>（详见 XXX）"]
```

**口诀**：**越私人越往 MEMORY，越团队越往 CLAUDE，越流程化越往 Skill**。

## 图 6：扩展机制选型

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
      Custom Command
    派独立专员干重活
      Subagent
    某事件自动触发
      Hook
    连接外部系统
      MCP
```

**口诀**：**CLAUDE.md 讲背景，Skill 讲流程，Command 给快捷键，Subagent 派替身，Hook 搞自动，MCP 接外网**。


---

<!-- chapter-nav -->

📖  [← 附录 C · Slash 命令全表](C-Slash命令全表.md)  ·  [📑 返回目录](../../README.md)  ·  [附录 E · FAQ 10 问 →](E-FAQ.md)
