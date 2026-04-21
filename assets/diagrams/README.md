# 插图管理清单（Diagram Manifest）

本目录是全书所有**视觉元素**（思维导图、流程图、ASCII 框线图、截图等）的**唯一索引**。
任何人要改一张图、换风格、或加新图，都从这里开始。

## 一、插图 ID 编码规则

每张插图有一个**全局唯一 ID**，写在 manuscript 里插图上方的 HTML 注释里，例：

```markdown
<!-- diagram: MM-01 -->
\`\`\`mermaid
…
\`\`\`
```

ID 前缀代表类型：

| 前缀 | 类型 | 当前状态 | 说明 |
|---|---|---|---|
| `MM-` | Mindmap（思维导图） | ✅ 启用 | Mermaid mindmap，当前全书主力插图类型 |
| `ASCII-` | ASCII 框线图 | 🔒 冻结 | 存量保留，不新增；未来可能升级为 mindmap 或移除 |
| `FC-` | Flowchart（决策流程图） | 🔒 冻结 | 存量保留（附录 D 图 1-5），不新增 |
| `EX-` | Excalidraw 手绘图 | 🚧 预留 | 未来可能启用 |
| `IMG-` | 截图 / 照片 / AI 插画 | 🚧 预留 | 未来可能启用（分 Mac/Windows） |

**规则**：
- ID 编号在**类型内递增**（MM-01、MM-02、MM-03…；ASCII-01、ASCII-02…）
- 编号**永不回收**（即使一张图被删除，它的 ID 不再给别的图用——便于 Git 历史追踪）
- ID 在本清单里登记后才算生效

## 二、当前插图清单

### MM-（Mindmap，思维导图）

| ID | 标题 | 章节位置 | 状态 | 风格版本 |
|---|---|---|---|---|
| MM-01 | 扩展机制选型 | 附录 D 图 6 | ✅ 已定版 | forest-v1 |
| MM-02 | Claude Code 四层记忆 | Ch 13 §13.1 | ✅ 已定版 | forest-v1 |
| MM-03 | 权限系统 5 档 | Ch 7 §7.2 | ✅ 已定版 | forest-v1 |
| MM-04 | 三款主力模型 | Ch 15 §15.1 | ✅ 已定版 | forest-v1 |
| MM-05 | 新手 10 大错误分类 | Ch 16 §本章小结 | ✅ 已定版 | forest-v1 |
| MM-06 | 12 个核心命令 | Ch 18 §18.2 | ✅ 已定版 | forest-v1 |
| MM-07 | 第 1 章 · 先把电脑准备好（章首导览） | Ch 1 开场后 | ✅ 已定版 | forest-v1 |
| MM-08 | 全书地图（整本书脉络一图看清） | 00-本书怎么读.md 开场后 | ✅ 已定版 | forest-v1 |
| MM-09 | 第 2 章 · 安装 Claude Code（章首导览） | Ch 2 开场后 | ✅ 已定版 | forest-v1 |
| MM-10 | 第 3 章 · 你的第一次对话（章首导览） | Ch 3 开场后 | ✅ 已定版 | forest-v1 |
| MM-11 | 第 4 章 · Claude Code 到底是什么（章首导览） | Ch 4 开场后 | ✅ 已定版 | forest-v1 |
| MM-12 | 第 5 章 · 让它读文件（章首导览） | Ch 5 开场后 | ✅ 已定版 | forest-v1 |
| MM-13 | 第 6 章 · 让它改文件（章首导览） | Ch 6 开场后 | ✅ 已定版 | forest-v1 |
| MM-14 | 第 7 章 · 跑命令与权限机制（章首导览） | Ch 7 开场后 | ✅ 已定版 | forest-v1 |
| MM-15 | 第 8 章 · 交互循环七步法（章首导览） | Ch 8 开场后 | ✅ 已定版 | forest-v1 |
| MM-16 | 第 9 章 · 计划模式与撤销（章首导览） | Ch 9 开场后 | ✅ 已定版 | forest-v1 |
| MM-17 | 第 10 章 · 信任校准（章首导览） | Ch 10 开场后 | ✅ 已定版 | forest-v1 |
| MM-18 | 第 11 章 · 你的数据去哪了（章首导览） | Ch 11 开场后 | ✅ 已定版 | forest-v1 |
| MM-19 | 第 12 章 · Claude 为什么会变糊涂（章首导览） | Ch 12 开场后 | ✅ 已定版 | forest-v1 |
| MM-20 | 第 13 章 · 三层记忆（章首导览） | Ch 13 开场后 | ✅ 已定版 | forest-v1 |
| MM-21 | 第 14 章 · 写好你的 CLAUDE.md（章首导览） | Ch 14 开场后 | ✅ 已定版 | forest-v1 |
| MM-22 | 第 15 章 · 模型与成本（章首导览） | Ch 15 开场后 | ✅ 已定版 | forest-v1 |
| MM-23 | 第 16 章 · 新手 10 大错误（章首导览） | Ch 16 开场后 | ✅ 已定版 | forest-v1 |
| MM-24 | 第 17 章 · 什么时候该停下来（章首导览） | Ch 17 开场后 | ✅ 已定版 | forest-v1 |
| MM-25 | 第 18 章 · 常用快捷命令全览（章首导览） | Ch 18 开场后 | ✅ 已定版 | forest-v1 |
| MM-26 | 第 19 章 · 输入技巧（章首导览） | Ch 19 开场后 | ✅ 已定版 | forest-v1 |
| MM-27 | 第 20 章 · Skills 入门（章首导览） | Ch 20 开场后 | ✅ 已定版 | forest-v1 |
| MM-28 | 第 21 章 · 自定义 Slash 命令（章首导览） | Ch 21 开场后 | ✅ 已定版 | forest-v1 |
| MM-29 | 第 22 章 · Subagents 入门（章首导览） | Ch 22 开场后 | ✅ 已定版 | forest-v1 |
| MM-30 | 第 23 章 · Hooks 入门（章首导览） | Ch 23 开场后 | ✅ 已定版 | forest-v1 |
| MM-31 | 第 24 章 · MCP 入门（章首导览） | Ch 24 开场后 | ✅ 已定版 | forest-v1 |
| MM-32 | 第 25 章 · 团队协作基础（章首导览） | Ch 25 开场后 | ✅ 已定版 | forest-v1 |
| MM-33 | 第 26 章 · 进阶能力速览（章首导览） | Ch 26 开场后 | ✅ 已定版 | forest-v1 |
| MM-34 | 第 27 章 · 下一步路线（章首导览） | Ch 27 开场后 | ✅ 已定版 | forest-v1 |
| MM-35 | 附录 A · Mac 终端速查（章首导览） | 附录 A 引言后 | ✅ 已定版 | forest-v1 |
| MM-36 | 附录 B · Windows PowerShell 速查（章首导览） | 附录 B 引言后 | ✅ 已定版 | forest-v1 |
| MM-37 | 附录 C · Slash 命令全表（章首导览） | 附录 C 引言后 | ✅ 已定版 | forest-v1 |
| MM-38 | 附录 D · 决策流程图（章首导览） | 附录 D 引言后 | ✅ 已定版 | forest-v1 |
| MM-39 | 附录 E · FAQ 10 问（章首导览） | 附录 E 引言后 | ✅ 已定版 | forest-v1 |
| MM-40 | 附录 F · 术语表（章首导览） | 附录 F 引言后 | ✅ 已定版 | forest-v1 |
| MM-41 | 附录 G · 报错自救手册（章首导览） | 附录 G 引言后 | ✅ 已定版 | forest-v1 |
| MM-42 | 附录 H · 桌面应用导览（章首导览） | 附录 H 引言后 | ✅ 已定版 | forest-v1 |
| MM-43 | 附录 I · 延伸阅读（章首导览） | 附录 I 引言后 | ✅ 已定版 | forest-v1 |
| MM-44 | 附录 J · Claude Opus 4.7 新手指南（章首导览） | 附录 J 引言后 | ✅ 已定版 | forest-v1 |

### ASCII-（冻结存量）

> 这些是首版成稿时用的 ASCII 框线图，按用户 2026-04-20 决定**保留不改**。
> 未来若要升级，先在此清单里把 ID 对应的那一行 "状态" 改为"升级中"，再动手。

| ID | 所在文件 | 数量（约） | 状态 |
|---|---|---|---|
| ASCII-CH02 | `manuscript/part1-从零起步/02-安装-Claude-Code.md` | 5 处 | 🔒 保留 |
| ASCII-CH03 | `manuscript/part1-从零起步/03-你的第一次对话.md` | 12 处 | 🔒 保留 |
| ASCII-CH08 | `manuscript/part2-日常使用/08-交互循环七步法.md` | 1 处 | 🔒 保留 |
| ASCII-CH11 | `manuscript/part3-深度概念/11-你的数据去哪了.md` | 19 处 | 🔒 保留 |
| ASCII-CH18 | `manuscript/part4-避坑与判断力/18-常用快捷命令全览.md` | 18 处 | 🔒 保留 |
| ASCII-CH19 | `manuscript/part4-避坑与判断力/19-输入技巧.md` | 11 处 | 🔒 保留 |
| ASCII-CH20 | `manuscript/part5-扩展能力/20-Skills入门.md` | 6 处 | 🔒 保留 |
| ASCII-CH21 | `manuscript/part5-扩展能力/21-自定义Slash命令.md` | 7 处 | 🔒 保留 |
| ASCII-CH24 | `manuscript/part5-扩展能力/24-MCP入门.md` | 6 处 | 🔒 保留 |

### FC-（Flowchart，冻结存量）

| ID | 标题 | 章节位置 | 状态 |
|---|---|---|---|
| FC-01 | 权限决策流程 | 附录 D 图 1 | 🔒 保留（handDrawn） |
| FC-02 | 模型选择流程 | 附录 D 图 2 | 🔒 保留（handDrawn） |
| FC-03 | Ctx% 应对流程 | 附录 D 图 3 | 🔒 保留（handDrawn） |
| FC-04 | 卡住原则流程 | 附录 D 图 4 | 🔒 保留（handDrawn） |
| FC-05 | 信息分层决策 | 附录 D 图 5 | 🔒 保留（handDrawn） |

## 三、给新增 mindmap 用的流程（3 步）

1. **复制模板**：从 [`_template-mindmap.md`](./_template-mindmap.md) 复制完整 Mermaid 代码块
2. **插入 manuscript**：粘到目标位置，上方加 `<!-- diagram: MM-XX -->` 注释（XX 是清单里下一个未用的编号）
3. **登记**：在本文件"MM-"表格尾部加一行

## 四、改变全局风格的流程

如果某天你想换掉 mindmap 的配色/字体/线条，唯一真源是 [`_style.md`](./_style.md)。

1. 在 `_style.md` 里更新目标参数（记得写明 `风格版本号` 递增，如 `forest-v2`）
2. 用文本批量替换工具找到所有现有 mindmap 的 `themeVariables` 块，替换成新值
3. 在本清单里把受影响 mindmap 的 "风格版本" 列批量更新为 `forest-v2`
4. 在 `修订日志.md` 里记一次"全局视觉升级"

## 五、未来可能扩展的类型

| 场景 | 对应 ID 前缀 | 启用条件 |
|---|---|---|
| 想画带分支标签的流程（mindmap 画不了） | 延伸 `FC-` 或新建 `FC2-` | 重新讨论视觉规范 |
| 需要手绘质感比喻图 | `EX-` | 建立 Excalidraw 工作流 |
| 需要加截图 | `IMG-MAC-` / `IMG-WIN-` | 和现有 `assets/images/{mac,windows}/` 整合 |
| 需要 AI 生成装饰插画 | `AI-` | 规定多语言策略 |

启用任何新类型前，先在本文件"一、插图 ID 编码规则"表格里登记前缀语义。
