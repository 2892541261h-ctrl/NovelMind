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

### T007：Project Config 只读配置接口基础

状态：DONE

负责人：Claude Code

范围：

- `backend/routers/project_config.py`
- `backend/schemas/project_config.py`
- `backend/services/project_config_service.py`
- `backend/main.py`

说明：

- 已接入 FastAPI。
- 已验证 `verify-all.ps1` 通过。

### T008：Writer Context 只读上下文预览基础

状态：DONE

负责人：Claude Code

范围：

- `backend/routers/writer.py`
- `backend/schemas/writer_context.py`
- `backend/services/writer_context_service.py`
- `tests/backend/services/test_writer_context_service.py`

说明：

- `next chapter preview` 可用。
- `prompt preview` 只做本地预览，不执行 AI 生成。
- 真正 AI 生成必须通过 `backend/ai/gateway.py`。
- `chapter_id` 命名延续已修复。
- `next_order` 推断已修复。
- `pytest` 结果为 6 passed。
- 已验证 `verify-all.ps1` 通过。

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

## 阶段 3A：参考小说驱动原创写作

### T060：修正参考小说功能定义

状态：TODO

负责人：Codex

范围：

- 将功能命名为“参考小说驱动原创写作 / Reference Novel Guided Original Writing”。
- 明确该功能不是续写参考小说、复制参考小说、改写参考小说、搬运参考小说人物或剧情换皮。
- 明确该功能是抽象参考小说的创作方向，再辅助生成用户自己的原创小说。
- 只更新规划和规则文档，不写业务代码。

验收：

```powershell
.\scripts\verify-all.ps1
```

### T061：设计 Reference Creation Profile 字段草案

状态：DONE

负责人：Codex

范围：

- 定义“参考创作档案 / Reference Creation Profile”。
- 字段至少包含 `reference_title`、`genre`、`worldbuilding_pattern`、`setting_rules`、`power_system_or_core_mechanism`、`character_archetypes`、`relationship_patterns`、`conflict_patterns`、`plot_progression_model`、`chapter_structure_pattern`、`writing_style_profile`、`pacing_profile`、`emotional_tone`、`reader_hook_patterns`、`taboo_or_avoid_rules`、`originality_rules`、`target_novel_direction`。
- 明确 Reference Creation Profile 是参考方向，Story Bible 是用户原创小说设定。
- 不创建数据库模型，不引入依赖。

产物：

- `docs/REFERENCE_CREATION_PROFILE_SPEC.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T062：设计参考小说导入流程

状态：DONE

负责人：Claude Code

范围：

- 设计参考小说文件导入边界和输入格式。
- 明确导入文件只用于分析抽象，不作为 Daily Writer 直接续写来源。
- 设计导入失败、重复导入、超大文件和编码异常的处理策略。
- 不实现前端页面，不创建复杂后端逻辑。

产物：

- `docs/REFERENCE_NOVEL_IMPORT_FLOW.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T063：设计长文本分章和分块理解流程

状态：DONE

负责人：Claude Code

范围：

- 设计参考小说按章节、场景或长度分块的策略。
- 设计分块摘要、跨块汇总和全书级抽象流程。
- 明确分块理解必须通过 `backend/ai/gateway.py` 调用 AI。
- 不实现具体 AI Provider。

产物：

- `docs/LONG_TEXT_CHUNKING_FLOW.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T064：设计参考小说分析 Prompt 草案

状态：DONE

负责人：Codex

范围：

- 设计用于提取 Reference Creation Profile 的 Prompt 文件草案。
- Prompt 必须要求抽象设定逻辑、人物类型、剧情模式、文风特征和爽点节奏。
- Prompt 必须禁止复制原文、搬运角色名、搬运完整剧情桥段或简单换皮。
- 不调用真实 AI，不写业务代码。

产物：

- `prompts/reference_novel_analysis_prompt.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T065：设计从 Reference Creation Profile 生成原创 Story Bible 的流程

状态：DONE

负责人：Claude Code

范围：

- 设计用户确认 Reference Creation Profile 后生成原创 Story Bible 的流程。
- 明确 Story Bible 中的世界观、角色、地点、时间线和风格必须属于用户原创小说。
- 设计用户确认、修改和拒绝生成结果的节点。
- 不创建数据库模型，不实现 API。

产物：

- `docs/STORY_BIBLE_FROM_REFERENCE_PROFILE_FLOW.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T066：设计 Daily Writer 读取 Reference Creation Profile 的规则

状态：DONE

负责人：Codex

范围：

- 明确 Daily Writer 不能直接续写参考小说。
- Daily Writer 应读取用户原创小说的 Story Bible、用户确认过的 Reference Creation Profile、已有章节内容和本章写作目标。
- 明确 Daily Writer 不应直接读取参考小说原文作为章节生成输入。
- 保留章节文件存在则失败、不覆盖的硬性规则。

产物：

- `docs/DAILY_WRITER_REFERENCE_PROFILE_RULES.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T067：设计原创性检查规则

状态：DONE

负责人：Codex

范围：

- 设计检查规则，防止直接复制参考小说原文。
- 设计检查规则，防止把参考小说简单换皮。
- 明确检查失败时必须阻止生成或要求人工处理。
- 不引入外部依赖。

产物：

- `docs/ORIGINALITY_CHECK_RULES.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T068：设计人物不照搬检查规则

状态：DONE

负责人：Codex

范围：

- 设计检查规则，防止直接搬运参考小说角色名。
- 设计检查规则，防止直接搬运参考小说角色组合和人物关系。
- 明确允许抽象人物类型，不允许复制具体人物。
- 不写业务代码。

产物：

- `docs/CHARACTER_COPY_GUARD_RULES.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

### T069：设计剧情不换皮检查规则

状态：DONE

负责人：Codex

范围：

- 设计检查规则，防止直接搬运参考小说完整剧情桥段。
- 设计检查规则，防止只替换名称、地点或能力体系的剧情换皮。
- 明确允许抽象冲突模式和章节推进方式，不允许复制具体剧情链条。
- 不写业务代码。

产物：

- `docs/PLOT_RESKIN_GUARD_RULES.md`

验收：

```powershell
.\scripts\verify-all.ps1
```

说明：

- T060 至 T069 是规划和设计拆分任务。
- 后续实现任务必须在这些任务完成后继续拆分，不能和设计任务混在一个 Pull Request 中。

## 阶段 3B：前端 MVP 基础

### T070：前端基础工程

状态：DONE

负责人：Claude Code

范围：

- Vite + React + TypeScript + Tailwind CSS 工程配置。
- 不引入大型 UI 库。
- 深色主题。
- 保证 `npm install` 和 `npm run build` 可用。

产物：

- `frontend/` 完整工程文件

### T071：基础布局和路由

状态：DONE

负责人：Claude Code

范围：

- Sidebar 左侧导航 + Topbar + 主内容区布局。
- react-router-dom 路由配置。
- 导航项：Dashboard、Projects、Story Bible、Characters、Chapters、Model Settings、Daily Writer。

产物：

- `frontend/src/components/Layout.tsx`、`Sidebar.tsx`
- `frontend/src/App.tsx`

### T072：API Client

状态：DONE

负责人：Claude Code

范围：

- 封装 fetch 请求，默认 `http://localhost:8000`。
- 支持 `VITE_API_BASE_URL` 环境变量。
- 提供 Projects/Characters/Chapters 的 CRUD 方法。

产物：

- `frontend/src/api/client.ts`
- `frontend/src/types/api.ts`

### T073：Projects 页面接入后端 CRUD

状态：DONE

负责人：Claude Code

范围：

- 项目列表、创建、删除。
- 项目详情页。
- 不绕过后端直接读写数据库。

产物：

- `frontend/src/pages/ProjectsPage.tsx`、`ProjectDetailPage.tsx`

### T074：Characters 页面接入后端 CRUD

状态：DONE

负责人：Claude Code

范围：

- 按项目列出角色、创建角色、删除角色。
- 项目选择器状态保存到 localStorage。

产物：

- `frontend/src/pages/CharactersPage.tsx`

### T075：Chapters 页面接入后端 CRUD

状态：DONE

负责人：Claude Code

范围：

- 按项目列出章节、创建章节、删除章节。
- 项目选择器状态保存到 localStorage。

产物：

- `frontend/src/pages/ChaptersPage.tsx`

## 阶段 3C：开发体验与本地联调

### T076：Windows 一键启动脚本

状态：DONE

负责人：Claude Code

范围：

- `scripts/start-backend.ps1`：自动进入 backend、使用 .venv、安装依赖、启动 FastAPI。
- `scripts/start-frontend.ps1`：自动进入 frontend、安装依赖、启动 Vite。
- `scripts/start-dev.ps1`：同时启动后端和前端（两个窗口）。

产物：

- `scripts/start-backend.ps1`
- `scripts/start-frontend.ps1`
- `scripts/start-dev.ps1`

### T077：本地开发环境说明

状态：DONE

负责人：Claude Code

范围：

- `scripts/check-env.ps1`：检查 Git、Python、.venv、Node.js、npm 和项目依赖。
- `README.md`：完整 Windows 本地运行说明，含环境要求、首次启动步骤、脚本说明。

产物：

- `scripts/check-env.ps1`
- `README.md`（重写）

### T078：前后端联调说明

状态：DONE

负责人：Claude Code

范围：

- `README.md` 中包含完整的后端接口表和前端页面状态表。
- 一键启动脚本 `start-dev.ps1` 实现前后端同时启动。
- `.env.example` 增加 `VITE_API_BASE_URL` 前端后端联调配置。

产物：

- `README.md`
- `.env.example`

### T079：检查脚本增强

状态：DONE

负责人：Claude Code

范围：

- `verify-all.ps1` 增强：优先使用 .venv Python、检查不应提交的构建产物（.venv/node_modules/dist/*.db）、后端编译检查、前端构建检查。

产物：

- `scripts/verify-all.ps1`（增强）

### T080：GitHub README 运行说明完善

状态：DONE

负责人：Claude Code

范围：

- `README.md` 完整重写：项目简介、已完成功能、技术栈、环境要求、首次启动、脚本说明、接口表、前端页面表、安全规则、项目文档索引。

产物：

- `README.md`

## 阶段 3D：参考小说引导原创写作基础

### T081：Reference Novel 数据模型

状态：DONE

负责人：Claude Code

范围：

- SQLAlchemy ORM 模型：ReferenceNovel（id, project_id, title, author, content, source_type, status）
- SQLAlchemy ORM 模型：ReferenceProfile（id, novel_id, project_id, genre, worldbuilding_pattern, character_archetypes, conflict_patterns, writing_style_profile, plot_progression_model, target_novel_direction, confidence, status）
- Pydantic schemas：Create/Update/Response

产物：

- `backend/models/reference_novel.py`、`reference_profile.py`
- `backend/schemas/reference_novel.py`、`reference_profile.py`

### T082：Reference Novel 服务层

状态：DONE

负责人：Claude Code

范围：

- CRUD 操作（create/read/update/delete/list）
- 参考小说分析生成 Reference Profile（通过 AI Gateway mock）
- Profile 的 CRUD 操作
- 分析结果包含：genre, worldbuilding, character archetypes, conflict patterns, writing style, plot progression, creative direction

产物：

- `backend/services/reference_novel_service.py`

### T083：Reference Novel API 路由

状态：DONE

负责人：Claude Code

范围：

- CRUD endpoints：list/create/get/update/delete
- POST /api/reference-novels/{id}/analyze — 调用 AI Gateway 生成 Reference Profile
- GET /api/reference-novels/{id}/profile — 获取 Profile
- 所有 AI 调用经过 backend/ai/gateway.py

产物：

- `backend/routers/reference_novels.py`

### T084：前端 Reference Novel 页面

状态：DONE

负责人：Claude Code

范围：

- 项目选择器 + 参考小说列表
- 粘贴/输入参考小说文本
- 查看分析生成的 Reference Profile
- 删除参考小说和 Profile
- 导航入口：Sidebar + App 路由

产物：

- `frontend/src/pages/ReferenceNovelPage.tsx`

### T085：集成与文档

状态：DONE

负责人：Claude Code

范围：

- main.py 挂载 reference_novels_router
- App.tsx 路由配置
- Sidebar 导航链接
- TASKS.md 记录 T081-T085

产物：

- `backend/main.py`、`frontend/src/App.tsx`、`frontend/src/components/Sidebar.tsx`

## 阶段 3E：Reference Profile 接入写作上下文

### T086：代码结构审查

状态：DONE

负责人：Claude Code

范围：

- 检查 writer_context_service、writer router、writer_context schema、reference_novel_service 等已有代码。
- 确认接入点：WriterContext schema + build_writer_context() + DailyWriterPage。

### T087：项目级 Reference Profile 读取

状态：DONE

负责人：Claude Code

范围：

- `reference_novel_service` 新增 `get_latest_profile_for_project(project_id)`。
- 优先返回最新生成的 ReferenceProfile。

产物：

- `backend/services/reference_novel_service.py`

### T088：注入 Writer Context

状态：DONE

负责人：Claude Code

范围：

- WriterContext schema 新增 `ReferenceProfileSummary`（含 genre、worldbuilding_pattern、character_archetypes、conflict_patterns、writing_style_profile、plot_progression_model、target_novel_direction）
- 包含 5 条原创性约束
- `build_writer_context()` 新增 DB 查询，注入 reference_profile
- 仅当 project_id 为整数时查询 DB

产物：

- `backend/schemas/writer_context.py`
- `backend/services/writer_context_service.py`

### T089：前端 Reference Profile 指示器

状态：DONE

负责人：Claude Code

范围：

- DailyWriterPage 检查当前项目是否有 Reference Profile。
- 有则显示"已接入参考创作画像"（绿色），无则提示去 Ref Novels 页面分析。

产物：

- `frontend/src/pages/DailyWriterPage.tsx`

### T090：文档与验证

状态：DONE

负责人：Claude Code

范围：

- TASKS.md 记录 T086-T090。
- verify-all.ps1 通过。

产物：

- `TASKS.md`

## 阶段 3F：Daily Writer MVP 写作闭环

### T091-T120：Daily Writer MVP 写作闭环 + 章节草稿管理

状态：DONE

负责人：Claude Code

范围：

- ChapterDraft ORM 模型（id, project_id, chapter_number, title, content, status, source, writing_goal, prompt_snapshot, context_snapshot）
- ChapterDraft Pydantic schema（Create/ListItem/Read/GenerateRequest/GenerateResponse）
- ChapterDraft service（CRUD + generate_draft 通过 AI Gateway）
- Daily Writer prompt builder（Reference Profile 接入 + 原创性约束）
- Daily Writer API（POST /generate, GET/DELETE /chapters）
- 章节防覆盖保护（project_id + chapter_number 已有则 409）
- 前端 DailyWriterPage（生成表单 + 草稿列表 + 内容查看 + 删除确认 + Reference Profile 状态）
- TASKS.md 更新

后端产物：

- `backend/models/chapter_draft.py`
- `backend/schemas/chapter_draft.py`
- `backend/services/chapter_draft_service.py`
- `backend/services/daily_writer_service.py`
- `backend/routers/daily_writer.py`
- `backend/main.py`

前端产物：

- `frontend/src/pages/DailyWriterPage.tsx`

## 阶段 3G：MVP Release Candidate

### T121-T180：NovelMind MVP Release Candidate

状态：DONE

负责人：Claude Code

范围：

- 正式 Chapter 模型扩展（source_draft_id, word_count, published_at）
- 正式 Chapter DB CRUD service（list/create/update/delete/publish_draft）
- 草稿编辑 API（PATCH /api/daily-writer/chapters/{id}）
- 草稿发布为正式章节（POST /api/formal-chapters/publish-draft/{id}）
- 正式章节列表/详情 API
- 导出 API（Markdown/TXT）
- 前端 Tab 式 UI（Generate / Drafts / Published）
- 前端草稿编辑（title + content textarea + Save）
- 前端发布按钮（Publish → 正式章节，草稿保留）
- 前端正式章节列表 + 查看
- 前端 Export MD / Export TXT 按钮
- 章节防覆盖：草稿不覆盖草稿，发布不覆盖正式章节，编辑草稿不影响正式章节
- Reference Profile 保持进入生成上下文
- AI 调用全部通过 backend/ai/gateway.py

产物：

- `backend/models/chapter.py`（扩展）
- `backend/schemas/formal_chapter.py`
- `backend/services/formal_chapter_service.py`
- `backend/services/export_service.py`
- `backend/services/chapter_draft_service.py`（扩展 update_draft）
- `backend/routers/formal_chapters.py`
- `backend/routers/exports.py`
- `backend/routers/daily_writer.py`（扩展 PATCH）
- `backend/main.py`
- `frontend/src/pages/DailyWriterPage.tsx`
- `TASKS.md`

## 阶段 3H：MVP Stabilization & Release Prep

### T181-T220：MVP 稳定性验收 + Release Prep

状态：DONE

负责工具：Codex

范围：

- 从 `main` 创建本轮 T181-T220 stabilization 分支。
- 检查 MVP 路由表和 API 前缀，确认正式章节使用 `/api/formal-chapters`。
- 新增 `scripts/check-mvp-routes.ps1`，检查路由一致性、前端 API 路径、AI Gateway 调用链路和原创性约束。
- 将 MVP 路由一致性检查接入 `scripts/verify-all.ps1`。
- 新增 MVP 手动验收文档、演示流程文档和 Release Checklist。
- 更新 README 的 MVP RC 链路、检查命令和验收文档入口。
- 检查文档中正式章节 API 路径，保留旧章节模块的 `/api/chapters/{id}`，正式章节统一记录为 `/api/formal-chapters/{id}`。
- 确认没有新增用户系统、支付系统、云部署、多模型调度、Agent 调度平台、GitHub Actions 自动 PR、富文本编辑器或权限系统。

验收：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-mvp-routes.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1
git status --short
```

产物：

- `scripts/check-mvp-routes.ps1`
- `docs/MVP_SMOKE_TEST.md`
- `docs/MVP_DEMO_FLOW.md`
- `docs/RELEASE_CHECKLIST.md`
- `README.md`
- `TASKS.md`
- `scripts/verify-all.ps1`

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
