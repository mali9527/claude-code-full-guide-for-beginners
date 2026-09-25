# Claude Code 零基础入门指南

简体中文 · [English overview](README.en.md)（英文导览；正文为中文）

**不会编程，也能学会让 AI 读文件、改文件，处理日常工作。** 从打开终端讲起，Mac 与 Windows 分开说明，遇到报错有地方查。作者：**马力**。

**2026 年 9 月更新｜Opus 5.5 · Fable 5.1**<br>
新模型怎么选、自己的账号能不能用、费用怎么看，书里都有对应说明。

**[从零开始阅读](manuscript/00-前言/00-本书怎么读.md)** · **[新模型使用指南](manuscript/附录/J-Opus-4.7新手指南.md)** · [按需找章节](#从你现在的问题开始)

![Claude Code 零基础入门指南：从第一次对话，到处理日常工作](assets/social/cover-bilingual-20260925.png)

## 学会用它处理手头的工作

把几份资料里的要点找出来，按要求修改文件，把一项任务拆成可核对的步骤。本书从这些日常需要出发，带你学会把要求说清楚、检查结果，以及在它改错时找回文件。

全书有 **42 张手绘图解**；各章配有小结、动手任务和排错说明。需要时再学 Skills（可复用的任务手册）、子代理、Hooks（自动触发的小检查）与 MCP（连接外部服务），把常做的工作整理成自己的流程。

**觉得有用，欢迎点右上角 Star 收藏。** 下次选模型、查报错或设置工作流程时，可以直接回来找对应章节。

## 从你现在的问题开始

| 你的需要 | 建议入口 |
|---|---|
| 完全没用过，想从头学 | [本书怎么读](manuscript/00-前言/00-本书怎么读.md) → [账号与费用路径](manuscript/00-前言/01-免费用上Claude-Code.md) |
| 想知道 Opus 5.5、Fable 5.1 对自己有什么用 | [先认识现在的 Claude](manuscript/00-前言/00-本书怎么读.md#先认识现在的-claude) |
| 已经装好，想选模型、查费用 | [新模型使用指南](manuscript/附录/J-Opus-4.7新手指南.md) → [模型与成本](manuscript/part3-深度概念/15-模型与成本.md) |
| 想让它开始处理文件 | [第一次对话](manuscript/part1-从零起步/03-你的第一次对话.md) → [让它读文件](manuscript/part2-日常使用/05-让它读文件.md) |
| 担心它改错文件 | [权限机制](manuscript/part2-日常使用/07-让它跑命令加权限机制.md) → [计划与回退](manuscript/part2-日常使用/09-计划模式与撤销.md) |
| 遇到报错，想尽快继续 | [常见报错与自救手册](manuscript/附录/G-报错自救手册.md) |

也可打开[简体合订稿](全书.md)连续阅读，按[手绘插图索引](assets/illustrations/读图索引.md)查找概念，或从[桌面应用导览](manuscript/附录/H-桌面应用导览.md)了解图形界面。

## 全书目录

前言 + 第 0—27 章 + 附录 A—K。第一次系统学习，先读各章「主线」；有具体问题时，按上面的入口查阅。

<details>
<summary>展开完整目录 · 40 个单元</summary>

<!-- studio:toc -->
共 40 个单元，42 张图。

1. [前言：本书怎么读](manuscript/00-%E5%89%8D%E8%A8%80/00-%E6%9C%AC%E4%B9%A6%E6%80%8E%E4%B9%88%E8%AF%BB.md)
2. [第 0 章：先选好账号与费用路径](manuscript/00-%E5%89%8D%E8%A8%80/01-%E5%85%8D%E8%B4%B9%E7%94%A8%E4%B8%8AClaude-Code.md)
3. [第 1 章：先把电脑准备好](manuscript/part1-%E4%BB%8E%E9%9B%B6%E8%B5%B7%E6%AD%A5/01-%E5%85%88%E6%8A%8A%E7%94%B5%E8%84%91%E5%87%86%E5%A4%87%E5%A5%BD.md)
4. [第 2 章：安装 Claude Code](manuscript/part1-%E4%BB%8E%E9%9B%B6%E8%B5%B7%E6%AD%A5/02-%E5%AE%89%E8%A3%85-Claude-Code.md)
5. [第 3 章：你的第一次对话](manuscript/part1-%E4%BB%8E%E9%9B%B6%E8%B5%B7%E6%AD%A5/03-%E4%BD%A0%E7%9A%84%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%AF%B9%E8%AF%9D.md)
6. [第 4 章：Claude Code 到底是什么](manuscript/part1-%E4%BB%8E%E9%9B%B6%E8%B5%B7%E6%AD%A5/04-Claude-Code%E5%88%B0%E5%BA%95%E6%98%AF%E4%BB%80%E4%B9%88.md)
7. [第 5 章：让它读文件](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/05-%E8%AE%A9%E5%AE%83%E8%AF%BB%E6%96%87%E4%BB%B6.md)
8. [第 6 章：让它改文件](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/06-%E8%AE%A9%E5%AE%83%E6%94%B9%E6%96%87%E4%BB%B6.md)
9. [第 7 章：让它跑命令 + 权限机制](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/07-%E8%AE%A9%E5%AE%83%E8%B7%91%E5%91%BD%E4%BB%A4%E5%8A%A0%E6%9D%83%E9%99%90%E6%9C%BA%E5%88%B6.md)
10. [第 8 章：交互循环七步法](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/08-%E4%BA%A4%E4%BA%92%E5%BE%AA%E7%8E%AF%E4%B8%83%E6%AD%A5%E6%B3%95.md)
11. [第 9 章：计划模式与撤销——先规划，再正确回退](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/09-%E8%AE%A1%E5%88%92%E6%A8%A1%E5%BC%8F%E4%B8%8E%E6%92%A4%E9%94%80.md)
12. [第 10 章：信任校准——什么时候信，什么时候核对](manuscript/part2-%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8/10-%E4%BF%A1%E4%BB%BB%E6%A0%A1%E5%87%86.md)
13. [第 11 章：你的数据去哪了——隐私与数据流](manuscript/part3-%E6%B7%B1%E5%BA%A6%E6%A6%82%E5%BF%B5/11-%E4%BD%A0%E7%9A%84%E6%95%B0%E6%8D%AE%E5%8E%BB%E5%93%AA%E4%BA%86.md)
14. [第 12 章：Claude 为什么会变糊涂——上下文原理](manuscript/part3-%E6%B7%B1%E5%BA%A6%E6%A6%82%E5%BF%B5/12-Claude%E4%B8%BA%E4%BB%80%E4%B9%88%E4%BC%9A%E5%8F%98%E7%B3%8A%E6%B6%82.md)
15. [第 13 章：三层记忆——会话 / 自动记忆 / CLAUDE.md](manuscript/part3-%E6%B7%B1%E5%BA%A6%E6%A6%82%E5%BF%B5/13-%E4%B8%89%E5%B1%82%E8%AE%B0%E5%BF%86.md)
16. [第 14 章：写好你的 CLAUDE.md——全书最高杠杆的一章](manuscript/part3-%E6%B7%B1%E5%BA%A6%E6%A6%82%E5%BF%B5/14-%E5%86%99%E5%A5%BD%E4%BD%A0%E7%9A%84CLAUDE.md.md)
17. [第 15 章：模型与成本——怎么选、怎么算、怎么省](manuscript/part3-%E6%B7%B1%E5%BA%A6%E6%A6%82%E5%BF%B5/15-%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%88%90%E6%9C%AC.md)
18. [第 16 章：新手 10 大错误——看完能避开的坑](manuscript/part4-%E9%81%BF%E5%9D%91%E4%B8%8E%E5%88%A4%E6%96%AD%E5%8A%9B/16-%E6%96%B0%E6%89%8B10%E5%A4%A7%E9%94%99%E8%AF%AF.md)
19. [第 17 章：什么时候该停下来——不要和 AI 对抗](manuscript/part4-%E9%81%BF%E5%9D%91%E4%B8%8E%E5%88%A4%E6%96%AD%E5%8A%9B/17-%E4%BB%80%E4%B9%88%E6%97%B6%E5%80%99%E8%AF%A5%E5%81%9C%E4%B8%8B%E6%9D%A5.md)
20. [第 18 章：常用快捷命令全览——按场景找到入口](manuscript/part4-%E9%81%BF%E5%9D%91%E4%B8%8E%E5%88%A4%E6%96%AD%E5%8A%9B/18-%E5%B8%B8%E7%94%A8%E5%BF%AB%E6%8D%B7%E5%91%BD%E4%BB%A4%E5%85%A8%E8%A7%88.md)
21. [第 19 章：输入技巧——把效率榨干](manuscript/part4-%E9%81%BF%E5%9D%91%E4%B8%8E%E5%88%A4%E6%96%AD%E5%8A%9B/19-%E8%BE%93%E5%85%A5%E6%8A%80%E5%B7%A7.md)
22. [第 20 章：Skills 入门——把常用流程写成任务手册](manuscript/part5-%E6%89%A9%E5%B1%95%E8%83%BD%E5%8A%9B/20-Skills%E5%85%A5%E9%97%A8.md)
23. [第 21 章：自定义 Slash 命令——主动启动一份技能](manuscript/part5-%E6%89%A9%E5%B1%95%E8%83%BD%E5%8A%9B/21-%E8%87%AA%E5%AE%9A%E4%B9%89Slash%E5%91%BD%E4%BB%A4.md)
24. [第 22 章：Subagents 入门——把专项工作交给独立助手](manuscript/part5-%E6%89%A9%E5%B1%95%E8%83%BD%E5%8A%9B/22-Subagents%E5%85%A5%E9%97%A8.md)
25. [第 23 章：Hooks 入门——事件发生时，自动做一个小检查](manuscript/part5-%E6%89%A9%E5%B1%95%E8%83%BD%E5%8A%9B/23-Hooks%E5%85%A5%E9%97%A8.md)
26. [第 24 章：MCP 入门——连接一个确实需要的外部服务](manuscript/part5-%E6%89%A9%E5%B1%95%E8%83%BD%E5%8A%9B/24-MCP%E5%85%A5%E9%97%A8.md)
27. [第 25 章：团队协作基础——和同事一起用 Claude Code](manuscript/part6-%E8%9E%8D%E5%85%A5%E6%97%A5%E5%B8%B8/25-%E5%9B%A2%E9%98%9F%E5%8D%8F%E4%BD%9C%E5%9F%BA%E7%A1%80.md)
28. [第 26 章：进阶能力速览——按工作需要选路线](manuscript/part6-%E8%9E%8D%E5%85%A5%E6%97%A5%E5%B8%B8/26-%E8%BF%9B%E9%98%B6%E8%83%BD%E5%8A%9B%E9%80%9F%E8%A7%88.md)
29. [第 27 章：下一步路线——读完书只是起点](manuscript/part6-%E8%9E%8D%E5%85%A5%E6%97%A5%E5%B8%B8/27-%E4%B8%8B%E4%B8%80%E6%AD%A5%E8%B7%AF%E7%BA%BF.md)
30. [附录 A：Mac 终端速查](manuscript/%E9%99%84%E5%BD%95/A-Mac%E7%BB%88%E7%AB%AF%E9%80%9F%E6%9F%A5.md)
31. [附录 B：Windows PowerShell 速查](manuscript/%E9%99%84%E5%BD%95/B-Windows-PowerShell%E9%80%9F%E6%9F%A5.md)
32. [附录 C：常用 Slash 命令速查](manuscript/%E9%99%84%E5%BD%95/C-Slash%E5%91%BD%E4%BB%A4%E5%85%A8%E8%A1%A8.md)
33. [附录 D：决策流程图](manuscript/%E9%99%84%E5%BD%95/D-%E5%86%B3%E7%AD%96%E6%B5%81%E7%A8%8B%E5%9B%BE.md)
34. [附录 E：FAQ（常见问题 10 问）](manuscript/%E9%99%84%E5%BD%95/E-FAQ.md)
35. [附录 F：术语表](manuscript/%E9%99%84%E5%BD%95/F-%E6%9C%AF%E8%AF%AD%E8%A1%A8.md)
36. [附录 G：常见报错与自救手册](manuscript/%E9%99%84%E5%BD%95/G-%E6%8A%A5%E9%94%99%E8%87%AA%E6%95%91%E6%89%8B%E5%86%8C.md)
37. [附录 H：Claude Code 桌面应用简明导览](manuscript/%E9%99%84%E5%BD%95/H-%E6%A1%8C%E9%9D%A2%E5%BA%94%E7%94%A8%E5%AF%BC%E8%A7%88.md)
38. [附录 I：延伸阅读与来源致谢](manuscript/%E9%99%84%E5%BD%95/I-%E5%BB%B6%E4%BC%B8%E9%98%85%E8%AF%BB.md)
39. [附录 J：Fable 5.1 与 Opus 5.5 新手指南](manuscript/%E9%99%84%E5%BD%95/J-Opus-4.7%E6%96%B0%E6%89%8B%E6%8C%87%E5%8D%97.md)
40. [附录 K：第三方接入，先确认支持范围](manuscript/%E9%99%84%E5%BD%95/K-%E7%AC%AC%E4%B8%89%E6%96%B9%E6%A8%A1%E5%9E%8B%E6%8E%A5%E5%85%A5.md)
<!-- /studio:toc -->

</details>

## 阅读与使用

本书免费阅读；**使用 Claude Code 的账号与模型费用另计**。免费 Claude 聊天计划不自动包含 Code。先读[账号与费用路径](manuscript/00-前言/01-免费用上Claude-Code.md)，确认适合自己的使用方式。

<details>
<summary>内容范围与核验说明</summary>

本书按官方文档复核，内容核对范围为 **2026-09-24—25**，覆盖 **Opus 5.5、Fable 5.1**；新模型操作示例以 Claude Code **2.1.280 或更新版本**为基线。尚未完成 Mac / Windows 真实账号实测，具体范围见[版本与核验说明](docs/版本与核验说明.md)。

本页章节和[简体合订稿](全书.md)随当前维护稿更新；固定发行版本保留发布时的正文快照：

<!-- studio:release -->
当前维护稿以本仓库为准。

已公开正文：[v2026.09.1](https://github.com/mali9527/claude-code-full-guide-for-beginners/releases/tag/v2026.09.1)。
<!-- /studio:release -->

</details>

想接收正式版本更新，可选择 **Watch → Custom → Releases**。后续公开教程收录在[系列教程](docs/系列教程.md)。朋友也在学 Claude Code，可以把本页或解决他具体问题的章节发给他。

## 来源、反馈与许可

本书由作者独立编写，以官方文档核对产品事实。参考资料与致谢见[附录 I](manuscript/附录/I-延伸阅读.md)。

发现问题可通过[仓库 Issues](https://github.com/mali9527/claude-code-full-guide-for-beginners/issues)反馈，附上章节、客户端版本和脱敏错误信息。请勿提交密钥或私人会话。

内容许可：[CC BY-NC-SA 4.0](LICENSE)。
