# 贡献指南

感谢你愿意来帮忙改进这本书 💚

本书是一本**持续演进**的开源中文入门书。任何人都欢迎参与——不管你是来抓错字、提建议、补充案例，还是贡献新章节。

## 三种参与方式（按门槛从低到高）

### 1️⃣ 抓错字 / 报告错误（最简单）

发现错字、错误命令、失效链接、图片不显示……

→ 直接 [提一个 Issue](https://github.com/mali9527/claude-code-full-guide-for-beginners/issues/new/choose) 选"📝 内容错误 / 错字"。写清楚哪一页哪一段就行。

### 2️⃣ 提建议 / 提问题

- 哪里讲得不够清楚？
- 希望增加什么内容？
- 你在实际使用中遇到什么坑，觉得书里应该收录？

→ 提 Issue 选"💡 建议"或"❓ 使用问题"

### 3️⃣ 提交改动（PR）

从改一个错字到贡献一整章，流程一致：

```bash
# 1. Fork 本仓库
# 2. 克隆你的 Fork
git clone https://github.com/<你的用户名>/claude-code-full-guide-for-beginners.git
cd claude-code-full-guide-for-beginners

# 3. 从 main 建一个新分支
git checkout -b fix/typo-ch07

# 4. 改好后提交
git add <你改的文件>
git commit -m "fix(ch07): 修正 Windows 路径反斜杠错别字"
git push origin fix/typo-ch07

# 5. 在 GitHub 上发起 Pull Request
```

---

## 如果你要贡献新内容（不只是改错字）

请先花 10 分钟读下面这几份**权威规格**——它们是本书所有写作决策的源头：

| 文件 | 作用 | 什么时候必读 |
|---|---|---|
| [`需求文档.md`](./需求文档.md) | 全书权威规格（v2.1） | 贡献任何新章节前必读 §1-3 + §6（两条铁律） |
| [`写作规范.md`](./写作规范.md) | 每日写作 quick reference | 写任何新内容前翻一眼 |
| [`术语翻译表.md`](./术语翻译表.md) | 英文→生活化中文翻译的**唯一真源** | 只要写到任何技术词，都先查这里 |
| [`CLAUDE.md`](./CLAUDE.md) | 给 Claude Code 协作会话看的硬规则 | 用 Claude Code 辅助写作时必读 |
| [`templates/章节模板.md`](./templates/章节模板.md) | 新章节起始骨架 | 新建章节时 copy 这份 |
| [`assets/diagrams/README.md`](./assets/diagrams/README.md) | 插图管理清单 | 加 mindmap / 改图前必读 |

### 两条铁律（来自需求文档 §6.0，不可违反）

1. **新概念即时解释**：文中出现任何读者可能不知道的术语、按键、符号、路径，**必须当场解释**。不允许"看后面就懂了"的悬念。
2. **前 5 章颗粒度最细**：第 0-4 章每步都手把手、每步给预期结果、每步给失败兜底、Mac/Windows 各走完整流程。

### 文风

- 对话用粗体标 **"你"**、常规标 "Claude"
- 技术黑话禁用表见 [`写作规范.md`](./写作规范.md)
- 章末三件套（小结 / 动手 / 卡住了）一个都不能少——**不写"自我检测"测验题**（动手任务就是自测）

### 插图

- **只用 Mermaid mindmap**，不新增其他类型（ASCII / flowchart 等存量保留但不新增）
- 统一 `forest-v1` 风格（见 [`assets/diagrams/_style.md`](./assets/diagrams/_style.md)）
- 每张图必须带 `<!-- diagram: MM-XX -->` 定位注释，在 [`assets/diagrams/README.md`](./assets/diagrams/README.md) 清单里登记后才算生效

---

## 提交 PR 前自检清单

改了正文内容后：

- [ ] 用 [`术语翻译表.md`](./术语翻译表.md) 扫一遍术语一致性
- [ ] 涉及插图：在 [`assets/diagrams/README.md`](./assets/diagrams/README.md) 登记 / 更新
- [ ] 在 [`修订日志.md`](./修订日志.md) 加一条变更记录
- [ ] 如果改了单章，确认 [`全书.md`](./全书.md) 也要同步（重跑 `/tmp/build_book.py`）
- [ ] 本地 Markdown preview 确认渲染正常（尤其是 mermaid 图）

## 你不能用 AI 写全章然后丢过来吗？

可以，但请在 PR 描述里**明确说明**你用了哪个工具、做了哪些人工审校。AI 生成内容**必须经过人工通读与事实核对**——本书的价值在于"真的为零基础读者打磨过"，不在于"又多了一份 AI 批量生成的内容"。

---

## 许可协议

提交 PR 即视为你同意你的贡献以 [CC BY-NC-SA 4.0](./LICENSE) 协议发布（与本书整体许可一致）。

---

再次感谢。如果有问题不确定从哪开始，直接开一个 Issue 问就行——没有蠢问题。
