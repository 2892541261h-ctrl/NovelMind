# NovelMind MVP 1.0 Release Notes

NovelMind MVP 1.0 是本地可运行的长篇小说创作 MVP 封版状态。它聚焦一条完整的原创写作闭环：

Reference Novel -> Reference Profile -> Writer Context -> Daily Writer -> Chapter Draft -> Edit Draft -> Publish Formal Chapter -> View Formal Chapter -> Export Markdown / TXT

## 当前能力

- Windows 本地启动后端和前端。
- 使用统一 AI Gateway 入口管理 AI 调用。
- 管理项目、角色、章节、世界设定、大纲、伏笔和写作风格等基础数据。
- 保存参考小说，并生成 Reference Profile。
- 将 Reference Profile 接入 Writer Context 和 Daily Writer。
- 生成章节草稿。
- 查看、编辑、保存和删除章节草稿。
- 将草稿发布为正式章节。
- 查看、更新和删除正式章节。
- 导出正式章节为 Markdown / TXT。
- 通过 `scripts/check-mvp-routes.ps1` 检查 MVP 路由和关键链路。
- 通过 `scripts/final-release-check.ps1` 做本地最终封版检查。

## 核心链路

1. 用户创建或选择项目。
2. 用户导入参考小说。
3. 系统分析参考小说，生成 Reference Profile。
4. Daily Writer 读取 Writer Context 和 Reference Profile。
5. Daily Writer 生成用户原创小说的章节草稿。
6. 用户人工编辑草稿。
7. 用户发布草稿为正式章节。
8. 用户查看正式章节。
9. 用户导出 Markdown / TXT。

## 本地运行入口

环境检查：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
```

一键启动：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

最终封版检查：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

## 验收文档

- `docs/MVP_SMOKE_TEST.md`
- `docs/MVP_DEMO_FLOW.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/GITHUB_UPLOAD_GUIDE.md`
- `docs/MVP_ACCEPTANCE_REPORT_TEMPLATE.md`

## 已知限制

- 当前不是云部署版本。
- 当前不是多用户版本。
- 当前不是商业化版本。
- 当前没有支付、权限、多模型调度或 Agent 调度平台。
- 当前 AI Provider 可能仍为 mock/stub，或依赖本地配置。
- 当前没有真正上传 GitHub Release。
- 当前没有创建远程 tag。
- 当前前端是 MVP 级界面，不包含复杂富文本编辑器。

## 下一阶段计划

- 补充更完整的后端回归测试。
- 扩展真实 AI Provider 适配，但继续保持所有调用通过 `backend/ai/gateway.py`。
- 完善 Story Bible 与正式章节之间的同步体验。
- 增加更严格的原创性和防换皮检查。
- 优化前端交互与错误提示。
- 在确认安全边界后，再规划云部署、多用户、权限和商业化能力。
