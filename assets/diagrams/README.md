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
