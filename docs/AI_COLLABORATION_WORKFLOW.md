# AI 联合开发流程

本文档定义 Codex 桌面端、Claude Code 桌面端和人类开发者在 NovelMind 项目中的协作方式。

## 基本原则

- 先拆任务，再写代码。
- 先明确边界，再交给对应工具。
- 每个任务必须小到可以单独完成。
- 每次交接都必须留下可验证记录。
- 所有本地命令使用 Windows PowerShell。
- 参考小说驱动原创写作只能抽象创作方向，不能续写、复制、改写或换皮参考小说。

## 标准流程

### 1. 选择任务

从 `TASKS.md` 中选择一个 `TODO` 任务。

建议创建分支：

```powershell
.\scripts\new-task-branch.ps1 -TaskId T003 -Slug ai-gateway-placeholder
```

### 2. 明确负责人

- 工程流程、脚本、CI、任务拆分：交给 Codex。
- 后端业务、前端页面、数据模型、API、生成逻辑：交给 Claude Code。
- Reference Creation Profile 数据结构草案、Prompt 草案、原创性规则和校验脚本：交给 Codex。
- 参考小说导入、长文本分块、AI 分析流程、Story Bible 生成逻辑和 Daily Writer 接入：交给 Claude Code。

如果任务同时包含两类工作，必须继续拆分，不能混在一个任务中。

### 3. 执行任务

执行时必须遵守：

- 不提交 API Key。
- 不创建 `.env`。
- 不引入未讨论的依赖。
- 不实现任务范围之外的功能。
- 不覆盖已有章节。
- AI 调用只能通过 `backend/ai/gateway.py`。
- 不直接复制参考小说原文、角色名或完整剧情桥段。
- 不把参考小说简单换皮。

### 4. 参考小说驱动原创写作流程

正确流程：

```text
参考小说
-> AI 阅读理解
-> 生成 Reference Creation Profile
-> 用户确认创作方向
-> 生成用户原创小说的 Story Bible
-> Daily Writer 根据 Story Bible 写用户自己的小说
```

协作边界：

- Codex 先定义规则、任务、字段草案、Prompt 草案和检查要求。
- Claude Code 再实现参考小说导入、长文本分块、AI 分析、原创 Story Bible 生成和 Daily Writer 接入。
- Reference Creation Profile 是参考方向，Story Bible 是用户原创小说设定。
- Daily Writer 不能直接续写参考小说。
- Daily Writer 应读取用户原创小说的 Story Bible、用户确认过的 Reference Creation Profile、已有章节内容和本章写作目标。
- Daily Writer 不应直接读取参考小说原文作为章节生成输入。
- 所有 AI 调用仍必须通过 `backend/ai/gateway.py`。

### 5. 本地检查

任务完成后运行：

```powershell
.\scripts\verify-all.ps1
```

如果后续出现测试命令，也应由 `verify-all.ps1` 统一调用。

### 6. 交接

使用 `docs/HANDOFF_TEMPLATE.md` 填写交接内容。

必须说明：

- 完成了什么。
- 没有完成什么。
- 修改了哪些文件。
- 检查如何运行。
- 需要下一位工具或开发者注意什么。

## Codex 到 Claude Code 的交接

适用场景：

- Codex 已完成骨架、脚本、CI、任务拆分。
- 下一步需要实现后端、前端、数据模型或业务逻辑。

交接必须包含：

- 任务编号。
- Claude Code 只应修改的范围。
- 不应修改的工程规则。
- AI Gateway 入口限制。
- Daily Writer 章节覆盖限制。
- Reference Creation Profile 与 Story Bible 的边界。
- 参考小说不得续写、复制、改写或换皮的限制。

## Claude Code 到 Codex 的交接

适用场景：

- Claude Code 已完成业务实现。
- 需要 Codex 检查、修复构建、补充 CI 或审查。

交接必须包含：

- 新增业务入口。
- 运行命令。
- 已知风险。
- 需要添加的检查项。
- 是否涉及 AI 调用。
- 是否涉及章节写入。
- 是否涉及参考小说导入或 Reference Creation Profile。
- 是否需要原创性、人物不照搬或剧情不换皮检查。

## 冲突处理

如果规范、任务和实现发生冲突，优先级如下：

1. 安全规则：不提交密钥、不覆盖章节、AI 调用只走 gateway、不复制或换皮参考小说。
2. `AGENTS.md`。
3. `docs/DEVELOPMENT_RULES.md`。
4. `TASKS.md`。
5. 具体实现。

## Pull Request 要求

每个 Pull Request 应包含：

- 对应任务编号。
- 变更摘要。
- 验证命令。
- 风险说明。

示例：

```powershell
.\scripts\finish-task.ps1
```
