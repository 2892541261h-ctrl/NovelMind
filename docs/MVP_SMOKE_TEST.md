# NovelMind MVP Smoke Test

本流程用于 MVP RC 手动验收。目标是确认核心链路稳定：

Reference Novel -> Reference Profile -> Writer Context -> Daily Writer -> Chapter Draft -> Edit Draft -> Publish Formal Chapter -> View Formal Chapter -> Export Markdown / TXT

## 1. 启动本地服务

在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

预期结果：

- 后端运行在 `http://127.0.0.1:8000`
- 前端运行在 `http://127.0.0.1:5173`
- 没有创建 `.env`、`.db` 或导出小说文件

## 2. 打开页面并选择项目

1. 打开 `http://127.0.0.1:5173`
2. 进入 `Projects`
3. 创建一个演示项目，或选择已有项目
4. 记录项目的 `project_id`

预期结果：

- 项目可以创建或展示
- `selectedProjectId` 可以被前端记住

## 3. 导入参考小说并生成 Reference Profile

1. 打开 `Reference Novels`
2. 选择当前项目或输入对应 `project_id`
3. 粘贴一小段参考小说文本
4. 保存参考小说
5. 点击分析，生成 Reference Profile

预期结果：

- Reference Novel 被保存
- Reference Profile 被生成
- 页面不暗示续写、改写或换皮参考小说

## 4. 打开 Daily Writer

1. 打开 `Daily Writer`
2. 确认 `project_id` 输入框显示当前项目
3. 如未显示，手动输入 `project_id`
4. 确认 Reference Profile 状态显示为 connected 或可识别状态

预期结果：

- `project_id` 可以手动修改
- Daily Writer 继续读取当前项目上下文

## 5. 生成章节草稿

1. 在 `Generate` 标签页输入章节编号
2. 输入可选标题、写作目标和额外要求
3. 点击生成草稿

预期结果：

- 调用 `POST /api/daily-writer/generate`
- AI 生成只通过 `backend/ai/gateway.py`
- 同项目同章节号已有草稿时，默认不覆盖旧草稿
- 如需新版本，应由明确参数创建新草稿，不覆盖旧记录

## 6. 编辑并保存草稿

1. 打开 `Drafts` 标签页
2. 点击刚生成的草稿
3. 修改 title 或 content
4. 点击 Save

预期结果：

- 调用 `PATCH /api/daily-writer/chapters/{id}`
- 只更新当前草稿
- 不影响正式章节

## 7. 发布正式章节

1. 在草稿详情中点击 Publish
2. 发布成功后进入 `Published` 标签页

预期结果：

- 调用 `POST /api/formal-chapters/publish-draft/{id}`
- 创建正式 Chapter
- `source_draft_id` 记录来源草稿
- `published_at` 有发布时间
- 草稿仍然保留
- 同 `project_id + chapter_number` 已有正式章节时返回冲突，不覆盖正式章节
- 空草稿不能发布，或返回明确错误

## 8. 查看正式章节

1. 在 `Published` 标签页点击正式章节
2. 查看标题、正文、字数和发布时间

预期结果：

- 调用 `GET /api/formal-chapters/{id}`
- 不再调用正式章节旧路径 `/api/chapters/{id}`
- 旧 `/api/chapters/{id}` 仅保留给旧章节 CRUD

## 9. 导出 Markdown / TXT

1. 在 `Published` 标签页点击 Export MD
2. 点击 Export TXT

预期结果：

- Markdown 调用 `GET /api/exports/project/{id}/markdown`
- TXT 调用 `GET /api/exports/project/{id}/txt`
- 导出内容只包含正式章节，不包含草稿
- 章节按 `chapter_number` 排序
- 内容包含章节标题和正文
- 导出通过响应返回，不在仓库生成文件

## 10. 防覆盖验证

逐项确认：

- 生成同号草稿默认不覆盖旧草稿
- 编辑草稿只影响当前草稿
- 删除草稿不删除正式章节
- 发布草稿不覆盖已有正式章节
- 编辑正式章节不影响草稿
- 删除正式章节不删除草稿
- 导出默认只导出正式章节

## 11. 封版前命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-mvp-routes.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1
git status --short
```

预期结果：

- 三个脚本通过
- `git status --short` 为 clean
- 没有 `.env`、`.venv`、`node_modules`、`frontend/dist`、`*.db`、API Key、日志文件或导出小说文件被提交
