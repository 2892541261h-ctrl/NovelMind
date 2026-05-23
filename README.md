# NovelMind

NovelMind 是一个 AI 长篇小说创作平台。本仓库当前处于项目骨架阶段，只包含最小可运行后端、前端占位页面、小说示例目录和工程协作规则。

## 当前范围

- 后端：Python、FastAPI、Uvicorn、Pydantic，预留 SQLite。
- 前端：React、Vite、TypeScript、Tailwind CSS。
- AI：当前只允许 mock provider。
- Daily Writer：仅保留目录和配置占位，不生成小说正文。

## 后端启动

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```

默认地址：

```powershell
http://127.0.0.1:5173
```

## 本地检查

在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1
```

## AI 调用说明

- AI 调用统一入口为 `backend/ai/gateway.py`，外部模块不得直接引用 `providers` 子包。
- 当前只支持 mock provider（不调用网络、不读取 API Key）。
- 可通过 `GET /health/ai-mock` 验证 gateway 是否正常工作。

## Story Bible

Story Bible 是一个小说项目的完整设定文件，包含角色、地点、世界规则、剧情线和写作风格。以结构化 JSON 方式存储于 `novels/{project_id}/story-bible.json`。

示例文件：`novels/demo-project/story-bible.json`

`project_id` 只允许使用字母、数字、短横线和下划线，避免路径穿越。

通过以下接口访问：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/projects/demo-project/story-bible
```

## 安全规则

- 不创建 `.env`。
- 不提交真实 API Key。
- 所有 AI 调用只能通过 `backend/ai/gateway.py`。
- Daily Writer 不能覆盖已有章节。
- `novels/demo-project/automation.json` 默认关闭自动生成。
