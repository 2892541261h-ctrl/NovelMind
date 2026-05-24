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
- 在参考小说分析、Reference Creation Profile 生成或 Story Bible 生成流程中绕过 `backend/ai/gateway.py`。
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

## Reference Creation Profile 规则

Reference Creation Profile（参考创作档案）是从参考小说中提取出来的参考方向，不是用户原创小说本身，也不是参考小说的可续写上下文。

它至少包含以下字段：

- `reference_title`
- `genre`
- `worldbuilding_pattern`
- `setting_rules`
- `power_system_or_core_mechanism`
- `character_archetypes`
- `relationship_patterns`
- `conflict_patterns`
- `plot_progression_model`
- `chapter_structure_pattern`
- `writing_style_profile`
- `pacing_profile`
- `emotional_tone`
- `reader_hook_patterns`
- `taboo_or_avoid_rules`
- `originality_rules`
- `target_novel_direction`

与 Story Bible 的关系：

- Reference Creation Profile 是从参考小说中提取出来的“参考方向”。
- Story Bible 是用户自己的原创小说设定。
- Reference Creation Profile 可以辅助生成 Story Bible，但不能替代 Story Bible。
- Story Bible 中的人物、地点、组织、剧情线和章节目标必须属于用户原创小说。

正确工作流：

```text
参考小说
-> AI 阅读理解
-> 生成 Reference Creation Profile
-> 用户确认创作方向
-> 生成用户原创小说的 Story Bible
-> Daily Writer 根据 Story Bible 写用户自己的小说
```

禁止：

- 把 Reference Creation Profile 写成参考小说摘要合集。
- 把 Reference Creation Profile 当作参考小说续写大纲。
- 在 Reference Creation Profile 中保留可直接复用的参考小说原文段落。
- 在 Reference Creation Profile 中直接搬运参考小说角色名、专有名词或完整剧情桥段。

## 参考小说原创性规则

参考小说驱动原创写作必须遵守：

- 不能直接复制参考小说原文。
- 不能直接搬运参考小说角色名。
- 不能直接搬运参考小说完整剧情桥段。
- 不能把参考小说简单换皮。
- 可以抽象设定逻辑、人物类型、关系模式、冲突模式、章节推进方式、文风节奏和读者爽点。
- 生成结果必须服务于用户自己的原创 Story Bible 和原创章节。

任何原创性检查发现高风险时，流程必须失败或转入人工确认，不能自动继续生成。

## Daily Writer 规则

Daily Writer 是自动生成小说章节的流程，必须极度保守。

硬性规则：

- 不能覆盖已有章节。
- 写入前必须检查目标路径是否存在。
- 如果目标路径存在，必须失败。
- 不允许使用 `-Force` 覆盖章节正文。
- 不允许清空章节目录。
- 不允许直接续写参考小说。
- 不允许直接复制参考小说原文。
- 不允许直接搬运参考小说角色名或完整剧情桥段。
- 不允许把参考小说简单换皮。
- 如果使用参考创作档案，必须读取用户确认过的 Reference Creation Profile。
- 章节生成输入应包含用户原创小说的 Story Bible、用户确认过的 Reference Creation Profile、已有章节内容和本章写作目标。
- 参考小说原文不得作为 Daily Writer 的直接章节生成输入。
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
- Reference Creation Profile 数据结构草案。
- 参考小说分析 Prompt 文件草案。
- 原创性、人物不照搬、剧情不换皮等规则文档和校验脚本。

Codex 不应在未被明确要求时实现大段业务逻辑。

## Claude Code 工作规则

Claude Code 应优先处理：

- 后端业务逻辑。
- 前端页面。
- 数据模型。
- API 接口。
- Daily Writer 生成逻辑。
- 参考小说文件导入。
- 长文本分章和分块理解。
- AI 分析流程。
- 从 Reference Creation Profile 生成原创 Story Bible 的逻辑。
- Daily Writer 读取 Reference Creation Profile 的业务接入。

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
