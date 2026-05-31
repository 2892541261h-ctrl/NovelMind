# NovelMind

## V1 Final + UI Polish

NovelMind V1 Final 已进入本地完整封版状态，前端已按中文写作工作台体验完成主要界面中文化与视觉打磨。当前支持浅色/深色模式，主题选择会持久化到 `localStorage("novelmind-theme")`，刷新后保持用户选择。

本轮不改变后端业务链路、不改变 AI Gateway 规则、不新增依赖。后续可在当前本地封版基础上进入 Windows MSI 打包阶段。

## Windows MSI Installer Preview

NovelMind 提供 Windows MSI 安装器预览源码，位于 `installer/`。该预览版使用 WiX Toolset 构建，目标是提供本地安装、桌面快捷方式、开始菜单快捷方式和一键启动体验。

构建命令：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-msi.ps1
```

安装器预览版仍依赖本机已有 PowerShell、Python 和 Node.js，不是完全离线桌面应用。MSI 构建产物输出到 `installer/dist/NovelMind-V1-Setup.msi`，不得提交到 Git。真实 AI Key 仍应通过本机环境变量配置，不要打进安装包。

更多说明见 `docs/WINDOWS_INSTALLER_GUIDE.md`。

AI 长篇小说创作平台。支持多 AI Provider、Story Bible 小说设定、Reference Creation Profile 参考创作档案、Daily Writer 自动章节生成。

## 当前已完成功能

- **后端 CRUD API**：项目管理、角色、章节、世界设定、大纲、伏笔、写作风格（FastAPI + SQLAlchemy + SQLite）
- **AI Gateway**：统一 AI 调用入口，当前 mock provider，`backend/ai/gateway.py`
- **Story Bible**：小说世界观/角色/地点/规则/剧情线读取 API
- **Writer Context**：写作上下文预览（只读，不生成正文）
- **前端 MVP**：React + Vite + TypeScript + Tailwind CSS 深色主题界面
- **参考小说驱动原创写作**：完整规划设计文档（`docs/` 目录）

## MVP Release Candidate

当前 `main` 已进入 MVP Release Candidate。核心演示链路为：

Reference Novel -> Reference Profile -> Writer Context -> Daily Writer -> Chapter Draft -> Edit Draft -> Publish Formal Chapter -> View Formal Chapter -> Export Markdown / TXT

当前 MVP RC 支持：

- 参考小说保存与 Reference Profile 分析。
- Daily Writer 读取项目写作上下文与 Reference Profile。
- 章节草稿生成、列表、查看、编辑、删除和防覆盖。
- 草稿发布为正式章节，草稿与正式章节分离。
- 正式章节列表、详情、更新、删除。
- Markdown / TXT 导出，默认只导出正式章节。
- 正式章节 API 使用 `/api/formal-chapters`，避免与旧 `/api/chapters/{id}` 路由冲突。

MVP 验收和演示文档：

- `docs/MVP_SMOKE_TEST.md`
- `docs/MVP_DEMO_FLOW.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/GITHUB_UPLOAD_GUIDE.md`
- `RELEASE_NOTES.md`

## NovelMind v1.2

v1.2 在 MVP 写作闭环上补充长篇连续写作上下文和章节质量检查，仍然是本地 MVP 版本，不包含云部署、多用户、支付、多模型调度或复杂富文本编辑器。

v1.2 新增：

- Story Bible、人物卡、世界观条目、章节计划的 CRUD 入口。
- 章节摘要和伏笔/线索管理，用于长篇连续性追踪。
- Continuity snapshot/report，用于查看当前项目连续性状态、下一章建议和上下文完整度。
- Daily Writer 会读取 Story Bible、人物卡、世界观条目、章节计划、章节摘要和未解决伏笔。
- 章节质量检查支持草稿和正式章节 review，并返回评分、issues、suggestions 和目标达成检查。
- 改写建议只生成参考建议，不自动覆盖草稿正文。
- 发布前质量提醒用于辅助人工判断，不阻塞发布。

v1.2 仍需遵守：

- 所有 AI 调用只能通过 `backend/ai/gateway.py`。
- 正式章节 API 继续使用 `/api/formal-chapters`，不得退回 `/api/chapters/{id}`。
- 章节草稿和正式章节不会被自动覆盖。
- 参考小说只用于抽象规律，不得续写、复制、搬运角色或换皮。

## MVP 1.0 Final Release Prep

MVP 1.0 当前定位是本地最终封版状态，不是云部署、多用户或商业化版本。上传 GitHub 前必须先运行最终封版检查：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

不要跳过检查直接 push。上传前流程见 `docs/GITHUB_UPLOAD_GUIDE.md`，版本说明见 `RELEASE_NOTES.md`。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite, Pydantic |
| 前端 | React 18, Vite 6, TypeScript 5.7, Tailwind CSS 3.4 |
| AI | mock provider（不调用网络），统一入口 `backend/ai/gateway.py` |
| 测试 | pytest, FastAPI TestClient, 内存 SQLite |
| 平台 | Windows 本地开发 |

## 环境要求

- **Python 3.11+**（建议使用 `.venv` 虚拟环境）
- **Node.js 20+**（含 npm）
- **Git**

### Windows Python 注意事项

如果 `python` 命令打开 Microsoft Store 而不是运行 Python：

1. 打开 Windows 设置 → 应用 → 应用执行别名
2. 关闭 `python.exe` 和 `python3.exe` 的应用执行别名
3. 确保 Python 已通过官网安装并加入 PATH

## 首次启动

```powershell
# 1. 克隆仓库
git clone <repo-url>
cd NovelMind

# 2. 创建 Python 虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..

# 4. 安装前端依赖
cd frontend
npm install
cd ..
```

## 启动方式

### 一键开发启动

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

此命令会打开两个 PowerShell 窗口，分别运行后端和前端。

### 分别启动

```powershell
# 后端（http://127.0.0.1:8765）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1

# 前端（http://127.0.0.1:5173）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

### 手动启动

```powershell
# 后端
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload

# 前端
cd frontend
npm run dev
```

## 本地检查

```powershell
# 环境检查
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1

# MVP 路由和关键链路检查
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-mvp-routes.ps1

# 全量验证（含后端编译和前端构建）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1

# MVP 1.0 最终封版检查
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

## 后端接口

| 接口 | 说明 |
|---|---|
| `GET /health` | 健康检查 |
| `GET /api/ai/test` | AI Gateway mock 测试 |
| `GET /api/projects` | 项目列表 |
| `POST /api/projects` | 创建项目 |
| `GET /api/projects/{id}` | 项目详情 |
| `GET /api/projects/{id}/characters` | 角色列表 |
| `GET /api/projects/{id}/chapters` | 章节列表 |
| `GET /projects/demo-project/story-bible` | Story Bible |
| `GET /projects/demo-project/writer/context` | 写作上下文预览 |
| `GET /api/story-bible` | v1.2 Story Bible |
| `GET /api/character-cards` | v1.2 人物卡 |
| `GET /api/world-entries` | v1.2 世界观条目 |
| `GET /api/chapter-plans` | v1.2 章节计划 |
| `GET /api/chapter-summaries` | v1.2 章节摘要 |
| `GET /api/plot-threads` | v1.2 伏笔/线索 |
| `GET /api/continuity/snapshot` | v1.2 连续性快照 |
| `POST /api/chapter-reviews/review-draft/{id}` | v1.2 草稿质量检查 |
| `POST /api/chapter-reviews/review-formal/{id}` | v1.2 正式章节质量检查 |
| `POST /api/chapter-reviews/suggest-rewrite-draft/{id}` | v1.2 草稿改写建议 |
| `GET /api/ai/providers` | AI 服务商配置 |
| `POST /api/ai/providers/{id}/local-key` | 本机直填 API Key |
| `POST /api/ai/providers/{id}/test` | 测试 AI 连接 |
| `GET /api/ai/models` | AI 模型配置 |
| `GET /api/ai/usage-logs` | 调用日志 |
| `GET /api/ai/usage-logs/summary` | 调用统计与估算成本 |
| `GET /api/project-dashboard/summary` | 项目仪表盘摘要 |

完整接口列表见各 `backend/routers/*.py`。

## 前端页面

| 路由 | 页面 | 状态 |
|---|---|---|
| `/` | Dashboard | 已完成 |
| `/projects` | 项目管理 | 已完成 |
| `/projects/:id` | 项目详情 | 已完成 |
| `/characters` | 角色管理 | 已完成 |
| `/chapters` | 章节管理 | 已完成 |
| `/story-bible` | Story Bible / 人物卡 / 世界观 / 章节计划 / 摘要 / 伏笔 | v1.2 |
| `/model-settings` | AI 设置（服务商/模型/日志） | 已完成 |
| `/daily-writer` | Daily Writer / 连续性上下文 / 章节质量检查 | v1.2 |

## AI Key 配置模式

NovelMind 支持两种 API Key 配置方式：

### 环境变量模式（env_var）

在 AI 设置中填写 `api_key_env_var`（例如 `OAI_API_KEY`），后端从系统环境变量中读取真实 Key。适合团队共享或 CI 环境。

### 本机直填模式（direct_local）

在 AI 设置中选择"本机直填"，直接粘贴 API Key。Key 仅保存在你的电脑上（`%APPDATA%/NovelMind/secrets.local.json`），**不会提交到 GitHub**，**不会打进 MSI 安装包**，**不会出现在 Usage Log 中**。保存后页面只显示脱敏结果（如 `sk-****abcd`），永远不会明文返回完整 Key。

> 如果重装系统或换电脑，需要重新填写 API Key。

## 不要提交的文件

以下文件和目录已被 `.gitignore` 排除，不应提交到 Git：

- `.env` — 环境变量（含 API Key）
- `.venv/` — Python 虚拟环境
- `node_modules/` — 前端依赖
- `frontend/dist/` — 前端构建产物
- `*.db` — 本地 SQLite 数据库
- `__pycache__/` — Python 缓存
- `.pytest_cache/` — 测试缓存

## 安全规则

- 不创建 `.env`，不提交真实 API Key
- 所有 AI 调用只能通过 `backend/ai/gateway.py`
- Daily Writer 不能覆盖已有章节
- 参考小说用于抽象分析，不能直接续写、复制、改写或换皮
- `novels/demo-project/automation.json` 默认关闭自动生成

## 项目文档

- `TASKS.md` — 任务拆分与进度
- `ROADMAP.md` — 路线图
- `CHANGELOG.md` — 变更记录
- `AGENTS.md` — AI 协作规范
- `docs/` — 详细设计文档（参考小说分析、原创性规则等）
- `docs/MVP_SMOKE_TEST.md` — MVP 手动验收流程
- `docs/MVP_DEMO_FLOW.md` — MVP 演示流程
- `docs/RELEASE_CHECKLIST.md` — Release 检查清单
- `docs/GITHUB_UPLOAD_GUIDE.md` — GitHub 上传前指南
- `docs/MVP_ACCEPTANCE_REPORT_TEMPLATE.md` — MVP 验收记录模板
- `RELEASE_NOTES.md` — MVP 1.0 版本说明
