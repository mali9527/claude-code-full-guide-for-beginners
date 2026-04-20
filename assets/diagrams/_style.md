# Mindmap 风格唯一真源

本文件是全书 mindmap 视觉风格的**唯一真源**。更新风格时先改这里，再批量替换现有插图。

## 当前版本：`forest-v1`

**决策日期**：2026-04-20
**决策人**：项目作者
**Why**：追求 MindNode 思维导图软件的"清爽放射状"观感——白底、细浅线、大字号、苹果字体。
在 Mermaid 原生主题里做过对比（参见 `archive/experiments/mindmap-palette-compare.md` 的演化），
最终选定 **forest 主题 + 纤细变体**。

### 标准初始化块（复制这个）

```yaml
---
config:
  theme: forest
  themeVariables:
    fontFamily: "-apple-system, 'SF Pro Text', 'PingFang SC', 'Helvetica Neue', sans-serif"
    fontSize: "17px"
    lineColor: "#D9D9D9"
---
```

### 参数解读

| 参数 | 值 | 为什么是这个 |
|---|---|---|
| `theme` | `forest` | Mermaid 原生主题里最接近 MindNode 的；自动轮转绿系分支色 |
| `fontFamily` | `-apple-system, …, 苹方, …` | Apple 设备显示 SF Pro，中文落到苹方；Windows/Linux fallback 到 Helvetica Neue / 默认无衬线 |
| `fontSize` | `17px` | 比 Mermaid 默认（14px）大两号，让节点文字成为视觉主角 |
| `lineColor` | `#D9D9D9` | 极浅灰——MindNode 的招牌是"几乎看不见的连线"，避免线条抢戏 |

## 未来变更规则

**任何对这套参数的改动都算一次"版本升级"**。版本号按 `forest-v1 → forest-v2 → …` 递增，
或换主题时 `forest-v* → cool-v1` 等。升级流程：

1. 在本文件顶部新增 `## 当前版本：xxx-v2` 标题块，把旧版本移到"## 历史版本"区
2. 把新的标准初始化块写出来
3. 更新 manuscript 里所有现有 mindmap 的 init 块（建议用正则批量替换）
4. 在 [`README.md`](./README.md) 插图清单里把"风格版本"列批量更新
5. 在 `../修订日志.md` 记一笔"全局视觉升级：`forest-v1 → xxx-v2`"

## 历史版本

*(暂无，`forest-v1` 是首版)*
