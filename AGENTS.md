# NovelMind AI 协作规范

本文件定义 NovelMind 项目中 Codex 桌面端、Claude Code 桌面端和人类开发者的协作边界。所有参与者必须先阅读本文件，再开始任务。

## 项目目标

NovelMind 是一个 AI 长篇小说创作平台，后续将支持：

- 多 AI Provider。
- Story Bible 小说圣经。
- Daily Writer 每日自动生成小说章节。
- GitHub Actions 自动创建小说更新 Pull Request。
- Windows 本地开发。
- Codex 桌面端和 Claude Code 桌面端联合开发。

## 工具分工

### Codex 负责

- 项目骨架与工程结构。
- GitHub Actions 与 CI 检查。
- Windows PowerShell 自动化脚本。
- 任务拆分与交接文档。
- 代码审查。
- 构建、测试、检查失败的修复。
- Daily Writer 自动化流程编排。

### Claude Code 负责

- 后端业务逻辑。
- 前端页面。
- 数据模型。
- API 接口。
- Daily Writer 生成逻辑。
- 大段代码实现。

## 禁止事项

- 不提交 API Key、Token、Cookie、私钥或任何真实凭证。
- 不创建 `.env` 文件。
- 不把 AI Provider SDK 或 HTTP 调用散落在业务代码中。
- 不覆盖已有小说章节。
- 不在一个任务中同时实现多个大功能。
- 不在规范任务中创建复杂前后端业务代码。
- 不绕过 `scripts/verify-all.ps1` 的检查结果。

## AI 调用统一规则

后续所有 AI 调用只能通过：

```powershell
backend/ai/gateway.py
```

规则如下：

- 业务代码不得直接调用 OpenAI、Anthropic、Gemini、DeepSeek、本地模型或其他 AI Provider。
- 业务代码不得直接读取 AI Provider API Key。
- 新增 Provider 时，只能在 `backend/ai/gateway.py` 及其同目录适配层内扩展。
- 前端不得直接调用 AI Provider。
- GitHub Actions 和 Daily Writer 自动化只能调用后端封装入口，不得绕过 gateway。
- 审查代码时，发现任何绕过 `backend/ai/gateway.py` 的 AI 调用都必须退回修改。

## Daily Writer 章节安全规则

Daily Writer 必须遵守：

- 不能覆盖已有章节文件。
- 不能修改已经发布或已经合并的章节正文。
- 新章节必须使用新的章节编号或新的唯一文件名。
- 生成前必须检查目标章节路径是否已存在。
- 如果目标文件已存在，流程必须失败并提示人工处理。
- 自动创建 Pull Request 时，只能包含本次新增章节和必要元数据更新。
- Daily Writer 生成逻辑由 Claude Code 实现，自动化流程由 Codex 编排。

## 任务粒度

每个任务必须小到可以单独完成、单独检查、单独提交。推荐大小：

- 一个任务只改一个模块或一条流程。
- 一个任务应该能在一次 Pull Request 中清楚审查。
- 一个任务必须有明确验收标准。
- 大功能必须先拆成多个 `TASKS.md` 条目。

## 交接方式

每次交接必须包含：

- 当前任务编号。
- 已完成内容。
- 未完成内容。
- 修改过的文件。
- 如何运行检查。
- 风险和待确认事项。

交接模板见 `docs/HANDOFF_TEMPLATE.md`。

## Windows 开发约定

所有本地命令必须优先使用 Windows PowerShell。示例：

```powershell
.\scripts\verify-all.ps1
.\scripts\new-task-branch.ps1 -TaskId T001 -Slug project-docs
.\scripts\finish-task.ps1
```

如果某个命令只能在其他 shell 中运行，必须先在文档中说明原因，并提供 PowerShell 等价命令或替代方案。
