> **历史构建目录**：对应四月 PDF。该流程未接入九月的新清单，不用于导出当前版；历史 PDF 的确切源提交未知。当前维护方式见 [构建说明](../docs/维护构建.md)。

# pdf-build

用 **Typst + Pandoc** 把 `manuscript/` 下的 markdown 编译成 A5 印刷级 PDF。

## 要什么

```bash
brew install typst pandoc
brew install --cask font-sarasa-gothic font-jetbrains-mono  # 已有思宋/苹方的话不必装思源
npm install                                                 # 在 pdf-build/ 下装 mermaid-cli
```

## 构建流程

```bash
python3 pdf-build/extract_mermaid.py   # 从 manuscript/*.md 抽 44 个 Mermaid 到 diagrams/*.mmd
./pdf-build/node_modules/.bin/mmdc -i diagrams/MM-XX.mmd -o diagrams/MM-XX.png -b white --scale 3
# 或批量：
# ls pdf-build/diagrams/*.mmd | xargs -P 4 -I {} bash -c 'f="{}"; ./pdf-build/node_modules/.bin/mmdc -i "$f" -o "${f%.mmd}.png" -b white --scale 3'
python3 pdf-build/build.py              # 全流程：预处理 → pandoc → 拼接 → typst 编译
```

输出：`pdf-build/output/Claude-Code-零基础入门指南.pdf`

## 文件结构

| 文件 | 作用 |
|---|---|
| `template.typ` | 版式模板（页面 / 字体 / 标题 / 引用 / 表格 / 页眉页脚） |
| `preprocess.py` | 预处理 markdown：去 nav、把 Mermaid 代码块替换成 `![](diagrams/MM-XX.png)` |
| `extract_mermaid.py` | 从章节中抽取 Mermaid 代码 |
| `build.py` | 主流程：预处理 → pandoc → 后处理（补 `width: 100%`、`horizontalrule`）→ Typst |
| `diagrams/*.mmd` | 44 个 Mermaid 源（提交） |
| `diagrams/*.png` | 44 张预渲染 PNG（提交，3× DPI） |
| `chapters-md/`、`chapters-typ/`、`book.typ` | 构建中间产物（`.gitignore`） |
| `output/*.pdf` | 可分发的 PDF（提交） |

## 已知小毛病

- Typst 对变量字体 Source Han Sans SC VF 有告警（不影响渲染，用了 macOS 自带 PingFang SC 为主字体后只剩警告）
- pandoc 在每个标题下会加 `<label>` 标签，PDF 里看不到但源文件里能看到，不管
- Mermaid 的 `<foreignObject>` SVG 在 Typst 里不能直接渲染，所以改走 PNG 路线（3× DPI 能保清晰）
