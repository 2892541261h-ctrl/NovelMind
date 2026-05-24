# NovelMind MVP Demo Flow

本流程用于 5-10 分钟演示。重点展示 NovelMind 的 MVP 写作闭环，而不是展示大型平台能力。

## 演示目标

让观众看到：

- 参考小说不是续写来源。
- AI 从参考小说中提炼 Reference Profile。
- Daily Writer 使用写作上下文生成用户自己的原创草稿。
- 人类可以编辑草稿。
- 草稿可以发布为正式章节。
- 正式章节可以导出为 Markdown / TXT。

## 演示前准备

1. 运行检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-env.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-mvp-routes.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-all.ps1
```

2. 启动服务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

3. 打开前端：

```text
http://127.0.0.1:5173
```

## 5-10 分钟演示步骤

### 1. 打开 Dashboard

该看什么：

- 前端可以加载
- 后端 health / AI mock 状态可用

讲解重点：

- 当前使用 mock AI Provider。
- 所有 AI 调用统一走 `backend/ai/gateway.py`。

### 2. 创建或选择项目

进入 `Projects`，创建一个演示项目，或选择已有项目。

该看什么：

- 项目出现在列表中
- 可以得到当前项目的 `project_id`

### 3. 添加参考小说

进入 `Reference Novels`，输入当前 `project_id`，粘贴一段参考小说文本并保存。

讲解重点：

- 参考小说用于提炼方向。
- 不是续写，不是改写，不是换皮。

### 4. 生成 Reference Profile

点击分析参考小说。

该看什么：

- 页面生成 Reference Profile
- Profile 是抽象创作方向，不是原文搬运

讲解重点：

- Reference Profile 帮助理解类型、人物类型、冲突模式、节奏和风格方向。
- 用户原创 Story Bible / 写作上下文仍是创作主线。

### 5. 打开 Daily Writer

进入 `Daily Writer`。

该看什么：

- `project_id` 输入框可见
- 可以从 `localStorage.selectedProjectId` 初始化
- Reference Profile 状态可见
- 有 `Generate`、`Drafts`、`Published` 三个标签页

### 6. 生成章节草稿

在 `Generate` 标签页输入章节号、标题和写作目标，然后点击 Generate。

该看什么：

- 生成后进入草稿列表
- 草稿不会覆盖已有同号草稿
- 冲突时显示明确错误

讲解重点：

- Daily Writer 使用 Reference Profile 作为抽象方向。
- 生成内容必须服务于用户自己的原创小说。

### 7. 编辑草稿

打开 `Drafts` 标签页，点击草稿，修改标题或正文，点击 Save。

该看什么：

- 草稿内容可编辑
- 保存后仍是草稿
- 不影响正式章节

### 8. 发布正式章节

点击 Publish。

该看什么：

- 调用 `/api/formal-chapters/publish-draft/{id}`
- 发布后进入 `Published` 标签页
- 草稿仍然保留
- 正式章节不会覆盖已有正式章节

### 9. 查看正式章节

点击 `Published` 中的章节。

该看什么：

- 显示正式章节标题、正文、字数和发布时间
- 正式章节使用 `/api/formal-chapters`
- 旧 `/api/chapters/{id}` 不承担正式章节详情

### 10. 导出

点击 Export MD 和 Export TXT。

该看什么：

- 浏览器打开 Markdown / TXT 响应
- 导出只包含正式章节
- 草稿不会出现在导出内容中

## 演示收尾

强调当前 MVP 边界：

- 不做用户系统。
- 不做支付系统。
- 不做云部署。
- 不做多模型调度。
- 不做复杂富文本编辑器。
- 当前目标是稳定展示核心原创写作闭环。
