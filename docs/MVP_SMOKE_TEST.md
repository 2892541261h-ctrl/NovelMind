# NovelMind MVP Smoke Test

## V1 Final UI 检查补充

在执行核心链路前，先确认全站主要界面为中文写作工作台风格：Dashboard、Daily Writer、Story Bible、Reference Novel、AI Settings、Sidebar 和 Layout 均应可读。切换浅色/深色主题后刷新页面，主题应继续保持，且主要卡片、按钮、输入框、提示和表格在两种主题下都清晰可读。

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
5. 切换 `Generate`、`Drafts`、`Published` 标签页，确认旧错误或成功提示会被清理
6. 确认 v1.2 context bar 显示 Story Bible、人物卡、世界观、章节计划、下一章建议和 Continuity 状态

预期结果：

- `project_id` 可以手动修改
- Daily Writer 继续读取当前项目上下文
- 中文提示清晰，空 `project_id` 或非法章节编号不会发送生成请求
- 连续性状态缺少数据时不崩溃

## 5. 填写 Story Bible 连续性资料

1. 打开 `Story Bible`
2. 输入当前 `project_id`
3. 分别创建 Story Bible、人物卡、世界观条目、章节计划、章节摘要和伏笔/线索
4. 编辑并删除一个测试条目，确认不会影响草稿或正式章节

预期结果：

- 调用 `/api/story-bible`、`/api/character-cards`、`/api/world-entries`、`/api/chapter-plans`、`/api/chapter-summaries`、`/api/plot-threads`
- `chapter_number` 相关输入必须大于等于 1
- 删除 Story Bible 资料不会删除草稿或正式章节

## 6. 生成章节草稿

1. 在 `Generate` 标签页输入章节编号
2. 输入可选标题、写作目标和额外要求
3. 点击生成草稿

预期结果：

- 调用 `POST /api/daily-writer/generate`
- AI 生成只通过 `backend/ai/gateway.py`
- 生成中按钮禁用，避免重复点击
- 生成成功后出现明确成功提示，并可进入 `Drafts` 编辑
- Prompt 上下文包含 Story Bible、人物卡、世界观、章节计划、最近章节摘要和未解决伏笔
- 同项目同章节号已有草稿时，默认不覆盖旧草稿
- 如需新版本，应由明确参数创建新草稿，不覆盖旧记录

## 7. 编辑、检查并保存草稿

1. 打开 `Drafts` 标签页
2. 点击刚生成的草稿
3. 修改 title 或 content
4. 点击质量检查
5. 点击改写建议
6. 点击 Save

预期结果：

- 调用 `PATCH /api/daily-writer/chapters/{id}`
- 质量检查调用 `POST /api/chapter-reviews/review-draft/{id}`
- 改写建议调用 `POST /api/chapter-reviews/suggest-rewrite-draft/{id}`
- review 结果包含评分、issues、suggestions 和目标达成检查
- 改写建议不会自动覆盖草稿正文
- 只更新当前草稿
- 不影响正式章节
- 保存、删除失败时有明确错误提示；删除成功后不会继续显示旧草稿详情

## 8. 发布正式章节

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
- 发布成功后有明确提示
- 发布前质量提醒只辅助人工判断，不阻塞发布

## 9. 查看并检查正式章节

1. 在 `Published` 标签页点击正式章节
2. 查看标题、正文、字数和发布时间
3. 点击质量检查
4. 可点击删除正式章节，确认删除后不影响草稿

预期结果：

- 调用 `GET /api/formal-chapters/{id}`
- 正式章节 review 调用 `POST /api/chapter-reviews/review-formal/{id}`
- 不再调用正式章节旧路径 `/api/chapters/{id}`
- 旧 `/api/chapters/{id}` 仅保留给旧章节 CRUD
- 删除正式章节调用 `DELETE /api/formal-chapters/{id}`；删除成功后不会继续显示旧正式章节详情

## 10. 导出 Markdown / TXT

1. 在 `Published` 标签页点击 Export MD
2. 点击 Export TXT

预期结果：

- Markdown 调用 `GET /api/exports/project/{id}/markdown`
- TXT 调用 `GET /api/exports/project/{id}/txt`
- 导出内容只包含正式章节，不包含草稿
- 章节按 `chapter_number` 排序
- 内容包含章节标题和正文
- 导出通过响应返回，不在仓库生成文件

## 11. 防覆盖验证

逐项确认：

- 生成同号草稿默认不覆盖旧草稿
- 编辑草稿只影响当前草稿
- 删除草稿不删除正式章节
- 发布草稿不覆盖已有正式章节
- 编辑正式章节不影响草稿
- 删除正式章节不删除草稿
- 导出默认只导出正式章节

## 12. 封版前命令

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
