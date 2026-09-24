# Claude Code 零基础入门指南 · 协作入口

作品 claude-code。本书不是 Codex 教程。当前为 2026-09 内容更新工作稿，用户已授权 P0 接入和本书更新；其他产品仍待独立任务。

先读需求文档顶部的当期变更，再读 book.yaml、facts.yaml、写作规范.md、术语翻译表.md 和 tools/standards/。book.yaml 是顺序、前置、事实引用与图示登记的唯一来源。前言加第 0—27 章及附录 A—K 共 40 个单元，维持已有章节地址；J 的历史文件名不代表当前模型。

manuscript/ 是中文源稿；全书.md、章节受管导航、README 目录由 tools/studio.py build 生成，不手改。繁体由已提交源稿生成并记录 translations.yaml，人工用语修订进 translation-overrides.yaml，不伪造源提交或审读通过。旧 PDF 属历史版，来源未知就写未知。

零基础叙事优先：新概念当场解释，第 0—4 章逐步说明动作/预期/失败处理，Mac 与 Windows 分开写。每章保留小结、动手、排错；完整配置放附录或示例文件。界面依据在制作元数据记录，不在图上添加重复声明，不虚构实测。全书插图采用 notebook-pen-v1：细方格纸上的黑色中性笔手绘，界面也手绘。原有思维导图按迁移清单替换；规范与样张见 assets/illustrations/styles/notebook-pen-v1/。

资料核验用内置 Web；官方定产品事实，社区教程只补使用经验并注明来源。先保存受审源提交，再写 checks；编辑复核可由当前引擎完成，与真实操作和事实确认分别记录。另一实际引擎交叉审核默认不启用，仅由作者手动触发；未触发或不可用不影响推进、合入和发布。常规核验缺什么就待验。工作分支不自动合入 main，不自动推送、发布、发帖或替用户注册购买。

私有任务、研究全文、恢复记录在总控 private/claude-code/；公开仓只保留可核查摘要。独立克隆用本书 tools 快照，不依赖总控私有路径。主写负责人负责合并有明确文件边界的协作修订。

## 全项目统一插图

本书采用 notebook-pen-v1，与系列其他作品共用同一种不透明细方格纸、黑色中性笔手绘和黑白要求，界面及其箭头、按钮、标签也遵守；不添加重复版本注释。先读 tools/standards/illustrations.md；策略及纸底在 assets/illustrations/。使用 illustrations pack/import/select 生产和采用，交付前执行 illustrations status 并逐张看实物，核对纸型、格距、整体纸色、笔触、黑白与不透明性。新作品不得另选风格，旧图不能绕过登记直接插入正文。
