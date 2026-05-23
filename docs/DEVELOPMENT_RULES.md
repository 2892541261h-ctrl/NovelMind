# NovelMind 开发规则

## 语言和命令

- 文档说明使用中文。
- 本地命令使用 Windows PowerShell。
- 脚本文件使用 `.ps1`。
- 不要求开发者使用 Bash、Zsh 或其他 Unix shell。

## 仓库结构约定

后续建议结构：

```text
backend/
  ai/
    gateway.py
frontend/
docs/
scripts/
tests/
.github/
```

当前阶段只创建协作规范和脚本，不创建复杂前后端代码。

## AI 调用规则

所有 AI 调用必须统一通过：

```text
backend/ai/gateway.py
```

禁止：

- 在业务代码中直接调用 AI Provider SDK。
- 在前端直接调用 AI Provider。
- 在 GitHub Actions 中直接调用 AI Provider。
- 在 Daily Writer 中绕过 `backend/ai/gateway.py`。
- 在代码中硬编码模型 API Key。

允许：

- 在 `backend/ai/gateway.py` 中定义统一调用入口。
- 在 `backend/ai/` 内添加 Provider 适配层。
- 在文档中说明需要哪些环境变量，但不得创建 `.env` 或提交真实值。

## 密钥和配置

禁止提交：

- API Key。
- Token。
- Cookie。
- 私钥。
- `.env`。
- 真实生产配置。

如果需要说明配置方式，只能写文档示例，例如：

```powershell
$env:NOVELMIND_PROVIDER = "example-provider"
```

不得把真实值写入仓库。

## Daily Writer 规则

Daily Writer 是自动生成小说章节的流程，必须极度保守。

硬性规则：

- 不能覆盖已有章节。
- 写入前必须检查目标路径是否存在。
- 如果目标路径存在，必须失败。
- 不允许使用 `-Force` 覆盖章节正文。
- 不允许清空章节目录。
- 自动 PR 只能包含本次新增章节和必要索引更新。

推荐写入逻辑：

```powershell
if (Test-Path $TargetChapterPath) {
    throw "目标章节已存在，禁止覆盖：$TargetChapterPath"
}
```

## 任务拆分规则

每个任务必须满足：

- 一个清晰目标。
- 一个主要负责人。
- 一组明确文件范围。
- 一个验收命令。
- 可以单独提交和审查。

不允许：

- 一个任务同时做后端、前端、CI 和业务大改。
- 一个任务中顺手重构无关文件。
- 一个任务中引入多个无关依赖。

## Codex 工作规则

Codex 应优先处理：

- 工程结构。
- 自动化脚本。
- CI。
- 任务拆分。
- 审查。
- 构建修复。

Codex 不应在未被明确要求时实现大段业务逻辑。

## Claude Code 工作规则

Claude Code 应优先处理：

- 后端业务逻辑。
- 前端页面。
- 数据模型。
- API 接口。
- Daily Writer 生成逻辑。

Claude Code 必须遵守 Codex 建立的工程规则和检查脚本。

## 本地检查

标准检查命令：

```powershell
.\scripts\verify-all.ps1
```

收尾命令：

```powershell
.\scripts\finish-task.ps1
```

后续如果增加后端测试、前端测试或格式化检查，应统一接入 `scripts/verify-all.ps1`。

## 文档更新

完成任务后应更新：

- `TASKS.md` 中对应任务状态。
- `CHANGELOG.md` 中新增一条记录。
- 必要时更新 `ROADMAP.md`。
