# Claude Code 零基础入门指南

给不会编程、没用过终端、希望用 AI 处理实际工作的人。作者：**马力**。

从准备电脑、安装和第一次对话开始，逐步学习读文件、改文件、判断权限、管理上下文与记忆，再按需学习 Skills、子代理、Hooks 和 MCP。主线采用 Mac 与 Windows 的终端操作；桌面版另有导览。

**2026 年 9 月简体正式版**：内容复核截至 **2026-09-25**，已纳入 **Opus 5.5、Fable 5.1**，新模型示例使用 Claude Code **2.1.280 或更新版本**。本稿已逐章核对易变事实、命令与练习，并采用 **42 张手绘插图**。本次以官方文档复核作为操作说明的发行依据，未宣称完成 Mac / Windows 真实账号实测，具体范围见[版本与核验说明](docs/版本与核验说明.md)。

先选择你的阅读入口：

- **第一次接触**：从[前言](manuscript/00-前言/00-本书怎么读.md)与[第 0 章：账号与费用路径](manuscript/00-前言/01-免费用上Claude-Code.md)开始。
- **读过四月版**：先看[这次更新了什么](docs/2026-09更新导读.md)，再读[第 15 章：模型与成本](manuscript/part3-深度概念/15-模型与成本.md)和[附录 J：新模型指南](manuscript/附录/J-Opus-4.7新手指南.md)。
- **想连起来读**：[简体合订稿](全书.md)。本次只发行简体版。
- **按图查找**：[42 张插图索引](assets/illustrations/读图索引.md)，可打开原图放大，并回到对应章节。
- **偏好图形界面**：[附录 H：桌面应用导览](manuscript/附录/H-桌面应用导览.md)。

本书可在 GitHub 阅读。**使用 Claude Code 的账户与模型费用另计**；免费 Claude 聊天计划不自动包含 Code。

## 全书目录

前言 + 第 0—27 章 + 附录 A—K。章节中先读“主线”，需要时再回到“支线”。

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

## 版本与下载

本次正式发行范围为简体 Markdown：40 个单元、合订稿与 42 张手绘插图。操作说明按官方文档核对，核验结论与范围见[简体发行复核](docs/2026-09-25简体发行复核.md)。旧的章节地址保留；第 0 章与附录 J 的历史文件名不代表其当前内容。

[四月历史 PDF](pdf-build/output/Claude-Code-零基础入门指南.pdf)仍保留原入口。**该 PDF 不包含本次九月修订**，不要据它查询新模型、当前费用和权限行为；本次没有新版 PDF 附件。

<!-- studio:release -->
当前维护稿以本仓库为准。

尚未登记已公开的里程碑版本。
<!-- /studio:release -->

## 来源、反馈与许可

本书使用独立组织的中文解释与练习，以官方文档核对产品事实。早期参考教程是 Florian Bruniaux 的 [Claude Code Ultimate Guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)，更多来源与使用边界见[附录 I](manuscript/附录/I-延伸阅读.md)。

发现问题可通过[仓库 Issues](https://github.com/mali9527/claude-code-full-guide-for-beginners/issues)反馈，附上章节、客户端版本和脱敏错误信息。请勿提交密钥或私人会话。

内容许可：[CC BY-NC-SA 4.0](LICENSE)。

<details>
<summary>维护与协作说明</summary>

[协作入口](AGENTS.md) · [单书需求](需求文档.md) · [写作规范](写作规范.md) · [术语表](术语翻译表.md) · [修订日志](修订日志.md) · [工具说明](tools/README.md)

内容清单和引用关系由 `book.yaml` 管理，事实来源在 `facts.yaml`；本仓工具快照可独立运行。先保存源稿，再生成简体合订稿。繁体转换暂停，历史转换稿不属于本次发行范围。私有任务和完整研究记录留在系列总控，不进入书仓。

</details>
