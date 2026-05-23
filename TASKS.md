# NovelMind 任务拆分

任务必须小、可验证、可交接。每个任务建议单独分支、单独 Pull Request。

## 状态说明

- `TODO`：未开始。
- `DOING`：进行中。
- `REVIEW`：等待审查。
- `DONE`：已完成。
- `BLOCKED`：被阻塞。

## 阶段 0：协作基础

### T001：创建工程协作规范

状态：DONE

负责人：Codex

范围：

- `AGENTS.md`
- `ROADMAP.md`
- `TASKS.md`
- `CHANGELOG.md`
- `docs/AI_COLLABORATION_WORKFLOW.md`
- `docs/DEVELOPMENT_RULES.md`
- `docs/HANDOFF_TEMPLATE.md`
- `scripts/verify-all.ps1`
- `scripts/new-task-branch.ps1`
- `scripts/finish-task.ps1`
- `.codex/daily-code.md`
- `.codex/review.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T002：创建最小目录骨架

状态：TODO

负责人：Codex

范围：

- 创建 `backend`、`frontend`、`tests` 等基础目录。
- 不实现完整业务。
- 不引入依赖。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T003：创建 AI Gateway 占位文件

状态：TODO

负责人：Claude Code

范围：

- 创建 `backend/ai/gateway.py`。
- 只定义统一入口和清晰注释。
- 不接入真实 Provider。
- 不读取真实 API Key。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 1：项目骨架与检查

### T010：添加基础 CI 工作流

状态：TODO

负责人：Codex

范围：

- 添加 GitHub Actions 工作流。
- 在 Windows 环境运行 PowerShell 检查。
- 不运行不存在的业务测试。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T011：定义后端启动命令

状态：TODO

负责人：Claude Code

范围：

- 定义后端本地启动方式。
- 使用 PowerShell 命令记录在文档中。
- 不实现复杂业务。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T012：定义前端启动命令

状态：TODO

负责人：Claude Code

范围：

- 定义前端本地启动方式。
- 使用 PowerShell 命令记录在文档中。
- 不实现复杂页面。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 2：AI Provider 网关

### T020：设计 AI Gateway 请求响应结构

状态：TODO

负责人：Claude Code

范围：

- 设计统一请求结构。
- 设计统一响应结构。
- 明确错误格式。
- 所有 AI 调用只能经过 `backend/ai/gateway.py`。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T021：添加 AI 调用静态检查

状态：TODO

负责人：Codex

范围：

- 扩展 `scripts/verify-all.ps1`。
- 检查业务代码是否绕过 `backend/ai/gateway.py`。
- 不引入新依赖。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 3：Story Bible

### T030：设计 Story Bible 最小数据结构

状态：TODO

负责人：Claude Code

范围：

- 世界观。
- 角色。
- 地点。
- 时间线。
- 写作风格。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T031：创建 Story Bible 读取接口

状态：TODO

负责人：Claude Code

范围：

- 后端读取 Story Bible。
- 不实现复杂前端编辑器。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 4：Daily Writer

### T040：设计 Daily Writer 章节命名规则

状态：TODO

负责人：Codex

范围：

- 定义章节目录。
- 定义章节编号。
- 明确如果目标文件存在则失败。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T041：实现本地 Daily Writer 命令入口

状态：TODO

负责人：Claude Code

范围：

- 读取 Story Bible。
- 计算下一章路径。
- 通过 `backend/ai/gateway.py` 生成内容。
- 写入新文件。
- 绝不能覆盖已有章节。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T042：添加 Daily Writer 自动化检查

状态：TODO

负责人：Codex

范围：

- 检查章节生成流程是否有覆盖风险。
- 检查 Pull Request 内容是否只包含允许文件。

验收：

```powershell
.\scripts\verify-all.ps1
```

## 阶段 5：GitHub Actions 自动 PR

### T050：创建 Daily Writer GitHub Actions 草案

状态：TODO

负责人：Codex

范围：

- 定时触发。
- 手动触发。
- 调用 Daily Writer 命令。
- 创建 Pull Request。
- 不提交任何 API Key。

验收：

```powershell
.\scripts\verify-all.ps1
```
