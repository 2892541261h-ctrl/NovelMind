# NovelMind 路线图

本路线图只描述阶段目标，不替代 `TASKS.md` 中的可执行任务。所有阶段都必须以小任务推进。

## 阶段 0：工程协作基础

目标：建立 Codex、Claude Code 和人类开发者可共同遵守的工程流程。

范围：

- 创建协作规范。
- 创建开发规则。
- 创建任务拆分文件。
- 创建 Windows 检查脚本。
- 明确 AI 调用只能通过 `backend/ai/gateway.py`。
- 明确 Daily Writer 不能覆盖已有章节。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 1：最小项目骨架

目标：建立后端、前端、文档和自动化目录，但不实现完整业务。

范围：

- 后端目录骨架。
- 前端目录骨架。
- `backend/ai/gateway.py` 空实现或接口占位。
- 基础 CI。
- 基础测试命令约定。

主要负责人：

- Codex：目录、CI、检查脚本。
- Claude Code：必要的业务占位接口。

## 阶段 2：AI Provider 网关

目标：让所有 AI 调用统一进入 `backend/ai/gateway.py`。

范围：

- Provider 配置读取规则。
- Provider 路由接口。
- 请求和响应结构。
- 错误处理策略。
- 禁止业务层直接调用 Provider。

主要负责人：

- Claude Code：网关业务逻辑。
- Codex：检查脚本和代码审查规则。

## 阶段 3：Story Bible 小说圣经

目标：建立长篇小说创作所需的世界观、人物、地点、时间线和风格约束。

范围：

- Story Bible 数据模型。
- Story Bible 编辑与读取接口。
- Story Bible 在生成流程中的输入格式。

主要负责人：

- Claude Code：数据模型、API、页面。
- Codex：任务拆分、审查、CI。

## 阶段 3A：参考小说驱动原创写作

目标：支持用户提供参考小说，由 AI 抽象其创作方向，再辅助生成用户自己的原创小说设定，而不是续写、复制、改写或换皮参考小说。

核心概念：

- Reference Creation Profile（参考创作档案）：从参考小说中提取出来的参考方向。
- Story Bible（小说圣经）：用户自己的原创小说设定。

正确工作流：

```text
参考小说
-> AI 阅读理解
-> 生成 Reference Creation Profile
-> 用户确认创作方向
-> 生成用户原创小说的 Story Bible
-> Daily Writer 根据 Story Bible 写用户自己的小说
```

范围：

- 定义 Reference Creation Profile 字段和边界。
- 设计参考小说导入、分章、分块理解流程。
- 设计参考小说分析 Prompt。
- 设计从 Reference Creation Profile 生成原创 Story Bible 的流程。
- 设计 Daily Writer 读取 Reference Creation Profile 的规则。
- 设计原创性、人物不照搬、剧情不换皮检查规则。
- 明确所有 AI 调用仍必须通过 `backend/ai/gateway.py`。

主要负责人：

- Codex：规划文档、任务拆分、校验脚本、数据结构草案、Prompt 文件草案、规则文档。
- Claude Code：后端业务逻辑、文件导入、长文本分块、AI 分析流程、Story Bible 生成逻辑、Daily Writer 接入、前端页面。

## 阶段 4：Daily Writer 本地流程

目标：在本地安全生成新章节。

范围：

- 读取 Story Bible。
- 读取用户确认过的 Reference Creation Profile。
- 选择下一章。
- 调用 AI Gateway。
- 写入新章节文件。
- 如果目标章节已存在，则失败，不覆盖。
- 不直接续写参考小说，不复制参考小说原文、角色名或完整剧情桥段。

主要负责人：

- Claude Code：生成逻辑。
- Codex：脚本、检查、审查。

## 阶段 5：GitHub Actions 自动 PR

目标：让 Daily Writer 可以通过 GitHub Actions 创建小说更新 Pull Request。

范围：

- 定时任务。
- 章节生成命令。
- 变更检查。
- 自动创建 Pull Request。
- 失败时保留日志。

主要负责人：

- Codex：GitHub Actions 与自动化流程。
- Claude Code：Daily Writer 命令入口。

## 阶段 6：长篇写作质量闭环

目标：提升连续性、风格一致性和可审查性。

范围：

- 章节一致性检查。
- 人物状态校验。
- 伏笔和回收记录。
- 自动摘要和索引。

主要负责人：

- Claude Code：业务能力。
- Codex：审查规则和自动化质量门禁。
