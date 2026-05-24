# NovelMind Release Checklist

本清单用于 MVP RC 合并、演示或封版前检查。

## 1. 基础状态

- 当前分支基于最新 `main`
- 工作区没有非预期改动
- `git status --short` 为 clean
- 没有 merge conflict
- 没有未提交的本地修复

## 2. 必跑脚本

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-mvp-routes.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

通过标准：

- `check-env.ps1` 可完成检查
- `check-mvp-routes.ps1` 输出 all MVP route checks passed
- `verify-all.ps1` 输出 all checks passed
- `final-release-check.ps1` 输出 MVP 1.0 final release check passed
- 后端编译 OK
- 前端构建 OK

## 3. 不应提交

确认没有提交：

- `.env`
- `.env.local`
- `.venv/`
- `venv/`
- `node_modules/`
- `frontend/node_modules/`
- `frontend/dist/`
- `*.db`
- `backend/*.db`
- API Key、Token、Cookie、私钥或真实凭证
- 日志文件
- 大型临时文件
- 导出的 Markdown / TXT 小说文件

## 4. 路由检查

必须成立：

- `POST /api/daily-writer/generate`
- `GET /api/daily-writer/chapters?project_id=`
- `GET /api/daily-writer/chapters/{id}`
- `PATCH /api/daily-writer/chapters/{id}`
- `DELETE /api/daily-writer/chapters/{id}`
- `GET /api/formal-chapters?project_id=`
- `GET /api/formal-chapters/{id}`
- `PATCH /api/formal-chapters/{id}`
- `DELETE /api/formal-chapters/{id}`
- `POST /api/formal-chapters/publish-draft/{id}`
- `GET /api/exports/project/{id}/markdown`
- `GET /api/exports/project/{id}/txt`
- `POST /api/reference-novels/{id}/analyze`

必须避免：

- 正式章节 API 不得使用 `/api/chapters/{id}`
- 不得通过调整 router 注册顺序掩盖冲突
- 旧 `/api/chapters/{id}` 仅保留给旧章节 CRUD

## 5. AI Gateway 规则

- Daily Writer 生成必须通过 `backend/ai/gateway.py`
- Reference Profile 分析必须通过 `backend/ai/gateway.py`
- 前端不得直接调用 AI Provider
- 业务代码不得直接调用 OpenAI、Claude、Gemini 或其他 Provider SDK
- 业务代码不得直接读取真实 API Key

## 6. Reference Profile 链路

必须保持：

Reference Novel -> Reference Profile -> Writer Context -> Daily Writer

确认：

- Reference Novel 可以保存
- Reference Profile 可以分析生成
- Daily Writer prompt 仍读取项目级 Reference Profile
- 没有让 Daily Writer 退回无上下文生成

## 7. 原创性约束

Daily Writer prompt 必须继续表达：

- 不得续写参考小说
- 不得复制参考小说原文
- 不得复用参考小说专有角色、地名、组织名、剧情事件
- 只能抽象参考叙事节奏、冲突模式、世界观组织方式、人物关系结构、写作风格方向
- 必须服务于用户自己的原创小说

## 8. 防覆盖规则

必须成立：

- 生成同号草稿默认不覆盖旧草稿
- `allow_new_version=true` 创建新草稿，不覆盖旧草稿
- 编辑草稿只影响当前草稿
- 发布草稿不覆盖已有正式章节
- 编辑正式章节不影响草稿
- 删除草稿不删除正式章节
- 删除正式章节不删除草稿
- 导出默认只导出正式章节

## 9. 导出规则

必须成立：

- Markdown / TXT 默认只导出正式章节
- 不导出草稿
- 按 `chapter_number` 排序
- 包含章节标题和正文
- 不在仓库中生成导出文件

## 10. 本轮不得新增的大功能

确认没有新增：

- 用户系统
- 支付系统
- 云部署
- 多模型调度
- Agent 调度平台
- GitHub Actions 自动 PR
- 富文本编辑器
- 权限系统
