# 附录 C：Claude Code Slash 命令全表

> 用法：Claude Code 输入框里输 `/`，选命令。这里按用途分组。

## 上下文管理

| 命令 | 作用 | 本书哪讲 |
|-----|------|--------|
| `/clear` | 清空当前会话（Ctx 归零） | Ch 12 |
| `/compact` | 压缩对话为摘要（大幅降低 Ctx） | Ch 12 |
| `/status` | 看当前模型、Ctx%、用量 | Ch 15 |

## 安全网

| 命令 | 作用 | 本书哪讲 |
|-----|------|--------|
| `/plan` | 进计划模式（只出方案不动手） | Ch 9 |
| `/rewind` | 精确回退到某个状态 | Ch 9 |

## 模型与配置

| 命令 | 作用 | 本书哪讲 |
|-----|------|--------|
| `/model` | 切换模型（Sonnet / Opus / Haiku / Opus 1M） | Ch 15 |
| `/config` | 看 / 改 Claude Code 配置 | Ch 18 |
| `/permissions` | 管理权限白名单 | Ch 7 |

## 记忆与项目

| 命令 | 作用 | 本书哪讲 |
|-----|------|--------|
| `/memory` | 打开 MEMORY.md 管理界面 | Ch 13 |
| `/init` | 自动生成 CLAUDE.md（**不推荐**） | Ch 14 |

## 会话管理

| 命令 | 作用 | 本书哪讲 |
|-----|------|--------|
| `/help` | 所有命令说明 | Ch 18 |
| `/exit` | 退出 Claude Code | Ch 3 |
| `/resume` | 恢复上次会话 | Ch 3 |
| `/login` / `/logout` | 登录 / 登出 | Ch 2 |

## 特殊前缀（非 slash 但属于"特殊输入"）

| 前缀 | 作用 | 例 | 本书哪讲 |
|-----|------|---|--------|
| `!` | 直接跑 shell 命令 | `!git status` | Ch 19 |
| `@` | 引用文件 | `@CLAUDE.md` | Ch 5 |

## 常用组合套路

| 套路 | 步骤 |
|-----|------|
| Plan → Execute | `/plan` → 审方案 → 退出 plan → 执行 |
| Opus 规划 + Sonnet 执行 | `/model` Opus → 出方案 → `/model` Sonnet → 执行 |
| 中段压缩 | Ctx 50% → `/compact` → 继续 |
| Rewind 而非修补 | Claude 出错 → `/rewind` → 重新描述 |

## 自定义命令

自己的 `/xxx` 命令放在：
- 全局：`~/.claude/commands/xxx.md`
- 项目：`<项目>/.claude/commands/xxx.md`

详见 Ch 21。

## 注意

- 具体命令名和行为**可能因 Claude Code 版本而异**
- 出现新命令 / 某命令消失 → 跑 `/help` 看当前版本全表
- 自定义命令会和内置一起在 `/help` 输出里出现
