<div align="center">

<img src="./assets/cover.png" alt="Claude Code 零基础入门指南" width="820" />

# Claude Code 零基础入门指南

**一本写给完全零基础读者的 Claude Code 系统入门书** · **针对 Claude Opus 4.7 全面更新**
不会编程、没用过终端、没碰过 AI 编程工具，也能从零读到上手用。

📖 从**终端 / 命令行**入门讲起，覆盖 **安装配置 · 读文件 / 改文件 / 跑命令 · 权限机制 · 交互循环七步法 · 计划模式与撤销 · 信任校准 · 数据隐私 · 三层记忆 · CLAUDE.md · 模型与成本（Opus 4.7 / Sonnet / Haiku 选型） · Prompt 输入技巧 · Skills / 自定义 Slash 命令 / Subagents / Hooks / MCP 五大扩展 · 团队协作**，全程 **Mac / Windows 双平台**手把手，配 **44 张 Mermaid 思维导图**。专设 **附录 J** 集中讲 Opus 4.7 的新概念、effort 档位、分词器变化与新手坑。

<sub>🏷️ **关键词**：Claude Code 中文教程 · Claude Code 入门 · Claude Opus 4.7 · Opus 4.7 新手指南 · Opus 4.7 使用教程 · Claude Opus 4.7 中文 · effort xhigh · Anthropic · AI 编程 · AI 编程助手 · AI Coding · 智能编程 · 零基础 · 新手入门 · 命令行入门 · 终端教程 · Prompt 工程 · 提示词技巧 · Agentic AI · Subagents · MCP · Hooks · Skills · Mac 教程 · Windows 教程 · Claude Code tutorial · Claude Opus 4.7 guide · Claude Code Chinese guide · beginner-friendly · zero-to-hero · learn AI coding</sub>

[![Stars](https://img.shields.io/github/stars/mali9527/claude-code-full-guide-for-beginners?style=flat-square&color=5C9F5C&label=⭐%20Stars)](../../stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/mali9527/claude-code-full-guide-for-beginners?style=flat-square&color=5C9F5C&label=最近更新)](./修订日志.md)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-D5A021?style=flat-square)](./LICENSE)
![Language](https://img.shields.io/badge/语言-简体中文-D5A021?style=flat-square)
![Status](https://img.shields.io/badge/状态-持续更新中-brightgreen?style=flat-square)
![Word Count](https://img.shields.io/badge/字数-17万+-5C9F5C?style=flat-square)
![Chapters](https://img.shields.io/badge/章节-27章+10附录-5C9F5C?style=flat-square)
![Opus 4.7](https://img.shields.io/badge/针对-Claude%20Opus%204.7-D5A021?style=flat-square)

### [📖 一口气读完全书](./全书.md) &nbsp;·&nbsp; [📚 按章节读](#-完整目录) &nbsp;·&nbsp; [📕 下载 PDF（A5 · 15 MB）](./pdf-build/output/Claude-Code-零基础入门指南.pdf) &nbsp;·&nbsp; ⭐ **[点个 Star](../../stargazers) 支持本书持续更新**

</div>

---

> 🌐 **语言 / Language**： **简体中文（本页）** · [繁體中文](./zh-TW/README.md) · English（coming soon）

## 你是不是也遇到过这些

- 听说 **Claude Code 很强**，打开教程一看全是"打开终端"、"pip install"、"cd 目录"——**直接劝退**
- 装上了但**不敢让它改文件**，怕它把整个项目搞坏
- 用了两三次就觉得它**"变糊涂"**了，不知道为什么，也不知道怎么办
- 想深入用，但 **Skill / Subagent / MCP / Hook** 这一堆词看起来像天书
- 每次有问题都得去翻英文文档 / Discord，**中文资料**要么太旧要么太浅

**这本书就是写给这样的你的。**

我们假设你**完全零基础**——不会编程、没用过终端、没装过 AI 编程工具——然后**手把手**带你走完 27 章 + 10 份附录，从"把电脑准备好"开始，到最后能把 Claude Code **稳定用在自己的日常工作里**。

---

## ✨ 读完你会学会什么

不是"看完有个印象"，而是**真的能上手做**：

1. ✅ **正确安装与配置** Claude Code（Mac / Windows 双平台每一步都手把手）
2. ✅ 看懂 Claude Code **到底是什么**（而不是"就当它是黑盒子用"）
3. ✅ 熟练让它**读文件、改文件、跑命令**——以及如何**稳妥地授权**
4. ✅ 理解它为什么会"**变糊涂**"，并在糊涂之前就察觉信号
5. ✅ 掌握**三层记忆机制**（会话 / MEMORY / CLAUDE.md），让它越用越懂你
6. ✅ 用好**计划模式、撤销、信任校准**——绕开新手最常踩的 10 大坑
7. ✅ 按需上手 **Skills / Slash 命令 / Subagents / Hooks / MCP** 5 大扩展能力
8. ✅ 懂得**什么时候该停下来**，什么时候该让它继续
9. ✅ 写出人话版 prompt——而不是抄模板、背咒语
10. ✅ 读懂错误信息 + 学会自救——知道**什么时候该重开一局**

---

## 🎯 本书独特之处

|  |  |
|---|---|
| 🎓 **真正的零基础** | 不假设你会编程，不假设你用过终端。**从"怎么打开终端"开始讲** |
| 🖥️ **Mac / Windows 双平台全覆盖** | 每一步操作都给两套命令，**不让 Windows 用户靠猜** |
| 🗺️ **43 张思维导图** | 每章开头一张"章首导览"——**一眼看清全章结构**；重要概念另配专题导图 |
| ✍️ **动手任务驱动** | 每章末尾"动手做一做"——**不是让你抄一遍，而是让你真的在自己电脑上跑起来** |
| 🆓 **完全免费开源** | 全本书稿 + 插图源码都在这个仓库里，**欢迎 Fork、翻译、改编** |
| 🔄 **持续跟版更新** | 跟随 Claude Code 官方版本迭代同步修订，每次变更记录在 [修订日志](./修订日志.md) |

---

## 📚 这本书适合你吗？

| 你的情况 | 这本书 |
|---|---|
| 听过 AI 编程，但没实际用过 | ✅ 正合适 |
| 没写过代码 / 只会一点点 | ✅ 正合适 |
| 对 Mac / Windows 终端有模糊印象但不太敢用 | ✅ 正合适 |
| 想让 AI 帮你处理日常工作（非纯编程） | ✅ 正合适 |
| 已经熟练使用 Claude Code / Cursor / Copilot | ❌ 这本太基础了 |
| 想学纯编程入门（Python / JavaScript） | ❌ 这不是编程书 |

---

## 🚀 怎么开始读

有两种方式，挑一种顺手的：

<table>
<tr>
<td width="50%" valign="top">

### 📖 [一口气读完（全书合订版）](./全书.md)

所有章节拼在一个页面里，**从上滚到底就读完了**。

**适合**：想沉浸式从头读到尾、或在手机 / 平板上连续阅读。

</td>
<td width="50%" valign="top">

### 📚 [按章节读（见下方目录）](#-完整目录)

每章一个独立 URL，**方便收藏、分享单章、跳着读**。

**适合**：按章节做动手任务、或日后回来查某一章。

</td>
</tr>
</table>

> 💡 **建议**：首次通读**从第 0 章开始**顺着读，每章做完"动手任务"再进下一章。别跳章——前 5 章颗粒度最细，是整本书的地基。

---

## 🔥 不知道从哪开始？试试这 3 章

如果你想先"试读"感受一下本书风格，我们建议从这三章开始：

- 🌱 **[第 3 章 · 你的第一次对话](./manuscript/part1-从零起步/03-你的第一次对话.md)** — 手把手带你和 Claude Code 说第一句话，**每一步都有预期结果 + 失败兜底**
- 🧠 **[第 13 章 · 三层记忆](./manuscript/part3-深度概念/13-三层记忆.md)** — 理解 Claude "记性"的真相，**配 mindmap 一眼看穿**
- ⚠️ **[第 16 章 · 新手 10 大错误](./manuscript/part4-避坑与判断力/16-新手10大错误.md)** — 把别人踩过的坑一次看完，**省你半年学习成本**

---

## 📖 完整目录

### 前言
- [00 本书怎么读](./manuscript/00-前言/00-本书怎么读.md)

### 第一部分 · 从零起步
> 前 5 章是全书颗粒度最细的地方，每一步都有 Mac / Windows 分开的完整流程和失败兜底。

- [01 先把电脑准备好](./manuscript/part1-从零起步/01-先把电脑准备好.md)
- [02 安装 Claude Code](./manuscript/part1-从零起步/02-安装-Claude-Code.md)
- [03 你的第一次对话](./manuscript/part1-从零起步/03-你的第一次对话.md)
- [04 Claude Code 到底是什么](./manuscript/part1-从零起步/04-Claude-Code到底是什么.md)

### 第二部分 · 日常使用
> 掌握"读文件 / 改文件 / 跑命令"三件核心交互，加上权限机制、交互循环七步法、计划模式、撤销、信任校准——你就能安心用它处理日常任务了。

- [05 让它读文件](./manuscript/part2-日常使用/05-让它读文件.md)
- [06 让它改文件](./manuscript/part2-日常使用/06-让它改文件.md)
- [07 让它跑命令加权限机制](./manuscript/part2-日常使用/07-让它跑命令加权限机制.md)
- [08 交互循环七步法](./manuscript/part2-日常使用/08-交互循环七步法.md)
- [09 计划模式与撤销](./manuscript/part2-日常使用/09-计划模式与撤销.md)
- [10 信任校准](./manuscript/part2-日常使用/10-信任校准.md)

### 第三部分 · 深度概念
> 为什么 Claude 会变糊涂？记忆分几层？CLAUDE.md 怎么写才有效？这一部分讲清楚"为什么"。

- [11 你的数据去哪了](./manuscript/part3-深度概念/11-你的数据去哪了.md)
- [12 Claude 为什么会变糊涂](./manuscript/part3-深度概念/12-Claude为什么会变糊涂.md)
- [13 三层记忆](./manuscript/part3-深度概念/13-三层记忆.md)
- [14 写好你的 CLAUDE.md](./manuscript/part3-深度概念/14-写好你的CLAUDE.md.md)
- [15 模型与成本](./manuscript/part3-深度概念/15-模型与成本.md)

### 第四部分 · 避坑与判断力
> 新手最容易踩的 10 个坑、什么时候该停下来别让 AI 继续、怎么用好 Slash 命令和 prompt 技巧。

- [16 新手 10 大错误](./manuscript/part4-避坑与判断力/16-新手10大错误.md)
- [17 什么时候该停下来](./manuscript/part4-避坑与判断力/17-什么时候该停下来.md)
- [18 常用快捷命令全览](./manuscript/part4-避坑与判断力/18-常用快捷命令全览.md)
- [19 输入技巧](./manuscript/part4-避坑与判断力/19-输入技巧.md)

### 第五部分 · 扩展能力
> 当默认功能不够用：用 Skill 打包重复任务、用 Command 做快捷指令、用 Subagent 派替身、用 Hook 自动触发、用 MCP 接外部系统。

- [20 Skills 入门](./manuscript/part5-扩展能力/20-Skills入门.md)
- [21 自定义 Slash 命令](./manuscript/part5-扩展能力/21-自定义Slash命令.md)
- [22 Subagents 入门](./manuscript/part5-扩展能力/22-Subagents入门.md)
- [23 Hooks 入门](./manuscript/part5-扩展能力/23-Hooks入门.md)
- [24 MCP 入门](./manuscript/part5-扩展能力/24-MCP入门.md)

### 第六部分 · 融入日常
> 从"能用"到"用熟"：团队协作、进阶能力速览、下一步路线。

- [25 团队协作基础](./manuscript/part6-融入日常/25-团队协作基础.md)
- [26 进阶能力速览](./manuscript/part6-融入日常/26-进阶能力速览.md)
- [27 下一步路线](./manuscript/part6-融入日常/27-下一步路线.md)

### 附录（按需查阅）
- [A Mac 终端速查](./manuscript/附录/A-Mac终端速查.md) · 命令 + 快捷键 + 常见错误
- [B Windows PowerShell 速查](./manuscript/附录/B-Windows-PowerShell速查.md)
- [C Slash 命令全表](./manuscript/附录/C-Slash命令全表.md) · 按用途分组 + 组合套路
- [D 决策流程图](./manuscript/附录/D-决策流程图.md) · 权限 / 模型 / Ctx / 卡住 / 信息分层 / 扩展选型
- [E FAQ](./manuscript/附录/E-FAQ.md) · 10 个最高频问题
- [F 术语表](./manuscript/附录/F-术语表.md) · 40+ 英文词 + 本书概念
- [G 报错自救手册](./manuscript/附录/G-报错自救手册.md) · 分阶段速查
- [H 桌面应用导览](./manuscript/附录/H-桌面应用导览.md) · 终端 ↔ 桌面概念对照
- [I 延伸阅读](./manuscript/附录/I-延伸阅读.md) · 六级资源 + 90 天学习节奏
- [J Claude Opus 4.7 新手指南](./manuscript/附录/J-Opus-4.7新手指南.md) · **2026-04 新增** · 新特性 + effort 档位 + 分词器变化 + 5 大新手坑

---

## 💬 反馈 & 参与

读到觉得哪里不清楚、哪里有错、哪里可以写得更好——**欢迎告诉我**：

- 🐛 **发现错误 / 提出建议**：[提一个 Issue](../../issues/new)
- 💡 **贡献改进**：Fork 本仓库 → 改完 → 提 PR
- ⭐ **觉得这本书有用**：[点个 Star](../../stargazers)——每个 Star 都是我继续更新的动力
- 👀 **想第一时间看到更新**：点右上角 **Watch → Custom → Releases** 就行

> 这本书会**持续跟随 Claude Code 官方版本迭代同步修订**。如果你 Star 了，每次大版本更新你都能第一时间看到。

---

## 📊 项目状态

- **2026-04-19** · 正文全书首版成稿（27 章 + 9 附录 ≈ 17 万字）
- **2026-04-20** · 引入 Mermaid mindmap 插图机制，全书加入 43 张思维导图
- **2026-04-20** · 新增全书单页合订版 + 每章上下篇导航
- **2026-04-21** · **新增附录 J：Claude Opus 4.7 新手指南**（配套 Anthropic 2026-04-16 发布的 Opus 4.7）
- **2026-04-22** · 新增 [繁體中文版](./zh-TW/README.md)（OpenCC s2twp 全书转繁）
- **2026-04-22** · 新增 **A5 书籍级 PDF**（Typst + Pandoc + Mermaid-CLI，376 页 / 15 MB）→ [下载](./pdf-build/output/Claude-Code-零基础入门指南.pdf)
- 详细版本记录见 [修订日志.md](./修订日志.md)

---

## 📝 关于这本书

- **作者**：马力（[@mali9527](https://github.com/mali9527)）
- **开源许可**：[CC BY-NC-SA 4.0](./LICENSE)——允许自由传播 / 修改 / 翻译，**禁止商用**，修改后必须保持同样协议开源。
- **多语言版本**：[繁體中文版](./zh-TW/README.md) 已上线；英文版筹备中（详见 [LICENSE](./LICENSE) 里的翻译说明）。
- **引用本书**：欢迎引用 / 转载 / 用于公开课素材，请保留原始仓库链接即可。
- **想参与写作 / 改稿**：读 [CONTRIBUTING.md](./CONTRIBUTING.md)，从改一个错字到贡献整章都欢迎。

---

<details>
<summary><b>🛠  如果你是来参与写作 / 改稿的</b></summary>

本书是一个正在演化的书稿项目。参与写作前请先读：

- [需求文档.md](./需求文档.md) — **权威规格**，所有写作决策的源头。尤其是 §1-3（背景、读者画像、学习目标）和 §6（两条铁律）
- [写作规范.md](./写作规范.md) — 每日写作的 quick reference
- [术语翻译表.md](./术语翻译表.md) — 术语→生活化翻译的唯一真源
- [templates/章节模板.md](./templates/章节模板.md) — 新写章节的起始模板
- [assets/diagrams/README.md](./assets/diagrams/README.md) — 插图管理清单与规范
- [CLAUDE.md](./CLAUDE.md) — 协作硬规则（给 Claude Code 会话看）

写完新章节后：

1. 用术语翻译表扫一遍一致性
2. 更新 [修订日志.md](./修订日志.md)
3. 如果涉及插图，去 `assets/diagrams/README.md` 登记
4. 重跑 `/tmp/build_book.py` 同步 `全书.md` 和章末导航

</details>

<div align="center">

---

**如果这本书对你有帮助，[给个 ⭐ Star](../../stargazers) 就是最好的鼓励。**

</div>
