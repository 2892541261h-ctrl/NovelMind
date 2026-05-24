# NovelMind

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
# 后端（http://127.0.0.1:8000）
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

完整接口列表见各 `backend/routers/*.py`。

## 前端页面

| 路由 | 页面 | 状态 |
|---|---|---|
| `/` | Dashboard | 已完成 |
| `/projects` | 项目管理 | 已完成 |
| `/projects/:id` | 项目详情 | 已完成 |
| `/characters` | 角色管理 | 已完成 |
| `/chapters` | 章节管理 | 已完成 |
| `/story-bible` | Story Bible | 占位 |
| `/model-settings` | 模型设置 | 占位 |
| `/daily-writer` | Daily Writer | MVP RC |

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
