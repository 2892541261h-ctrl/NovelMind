# NovelMind MVP 1.0 Release Notes

## V1 Final + UI Polish 更新记录

V1 Final 是当前本地完整封版状态。本轮重点是 UI 中文化、浅色/深色模式和演示体验打磨，不新增大型业务功能，也不改变 AI Gateway 调用规则。

- 全站主要用户界面完成中文化，包括 Dashboard、Daily Writer、Story Bible、Reference Novel、AI Settings、Sidebar 和 Layout。
- 新增浅色/深色主题，主题选择持久化到 `localStorage("novelmind-theme")`。
- Dashboard、DailyWriterPage、Sidebar、Layout 和全局样式按中文写作工作台体验重写。
- 统一 card、button、badge、tab、toast、empty-state、sidebar-link 和 stat-card 等基础样式。
- 后端业务逻辑、AI Gateway 和 API 路径保持稳定。
- 下一阶段可进入 Windows MSI 本地安装包打包准备。

## Windows MSI Installer Preview 更新记录

新增 Windows MSI 安装器预览源码，目标是提供本地安装和一键启动体验，不新增业务功能。

- 新增 `scripts/launch-novelmind.ps1` 和 `NovelMind Launcher.bat`，用于启动本地后端、前端并打开 `http://localhost:5173`。
- 新增 `installer/build-msi.ps1`、`installer/NovelMind.wxs` 和 `installer/README.md`，优先使用 WiX Toolset 构建 MSI。
- 新增 `docs/WINDOWS_INSTALLER_GUIDE.md`，说明构建、安装、启动、依赖和 API Key 安全边界。
- 新增 `scripts/check-installer.ps1`，检查安装器源码和禁止提交 MSI/EXE/ZIP 构建产物。
- MSI 预览版仍依赖本机已有 PowerShell、Python 和 Node.js，不是完全离线桌面应用。

NovelMind MVP 1.0 是本地可运行的长篇小说创作 MVP 封版状态。它聚焦一条完整的原创写作闭环：

Reference Novel -> Reference Profile -> Writer Context -> Daily Writer -> Chapter Draft -> Edit Draft -> Publish Formal Chapter -> View Formal Chapter -> Export Markdown / TXT

## v1.1 更新记录

v1.1 是 MVP 1.0 之后的本地稳定性与体验增强版本，重点不是新增大型功能，而是提升演示可用性、错误反馈和写作输出质量。

- 优化 `Daily Writer` 中文界面、状态提示和关键按钮 loading 禁用，降低重复点击风险。
- 优化 `Reference Novels` 中文界面，修复 `BASE` 在声明前使用的问题。
- 切换标签页、删除草稿、删除正式章节后会清理过期状态，避免旧详情继续显示。
- 新增正式章节删除入口，并补充发布、保存、删除等成功提示。
- 增强 `Daily Writer` prompt 的中文写作质量要求，继续禁止续写、复制、搬运角色/地名/组织名/剧情事件或简单换皮。
- 增强 Reference Profile 分析 prompt，强调只提取抽象创作规律，不输出原文搬运或具体剧情链条。

## v1.2 更新记录

v1.2 是 Story Bible、连续写作和章节质量检查增强版本。它继续保持本地 MVP 边界，不新增云部署、多用户、支付、多模型调度或复杂富文本编辑器。

- 新增 Story Bible 后端与前端入口，支持 Story Bible、人物卡、世界观条目和章节计划。
- 新增章节摘要与伏笔/线索管理，供 Daily Writer 读取最近章节摘要和未解决伏笔。
- 新增 Continuity snapshot/report，用于展示下一章建议、上下文完整度和连续性健康度。
- Daily Writer prompt 读取 Reference Profile、Story Bible、人物卡、世界观条目、章节计划、章节摘要和 Plot Threads。
- 新增章节质量检查：草稿 review、正式章节 review、目标达成检查、人物一致性检查、原创性风险提示和伏笔推进提醒。
- 新增草稿改写建议，建议内容不会自动覆盖草稿正文。
- 继续保留所有 AI 调用必须通过 `backend/ai/gateway.py` 的规则。
- 继续保持正式章节 API 使用 `/api/formal-chapters`，草稿 API 使用 `/api/daily-writer/chapters`。

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
