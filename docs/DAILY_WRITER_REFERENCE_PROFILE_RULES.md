# Daily Writer 读取 Reference Creation Profile 的规则

> 版本：0.1.0
> 状态：草案（尚未实现）
> 关联任务：T066

---

## 1. 功能定位

本文档定义 Daily Writer（每日自动章节生成器）在使用 Reference Creation Profile（参考创作档案）时必须遵守的读取规则和边界。

**核心原则：Daily Writer 的唯一任务是生成用户自己的原创小说章节，不是续写、改写或复刻参考小说。**

---

## 2. Daily Writer 可以读取哪些内容

### 2.1 必须读取（主要输入）

| 内容 | 来源 | 优先级 | 用途 |
|---|---|---|---|
| 用户原创 Story Bible | `novels/{project_id}/story-bible.json` | **最高** | 世界观、角色、地点、剧情线、风格约束 |
| 已有章节内容 | `novels/{project_id}/chapters/*.md` | **高** | 人物状态、剧情进度、上下文连续性 |
| 本章写作目标 | 自动化配置或用户指定 | **高** | 本章要推进哪条剧情线、完成什么目标 |
| 章节结构约束 | 系统规则 | **中** | 字数范围、命名规则、不覆盖约束 |

### 2.2 可以读取（参考输入）

| 内容 | 来源 | 优先级 | 用途 |
|---|---|---|---|
| Reference Creation Profile | `novels/{project_id}/_reference/reference_creation_profile.json` | **低** | 抽象写作方向参考（仅 style/pacing/hook 相关字段） |
| `writing_style_profile` | 从 Reference Creation Profile 中 | 低 | 基调、叙事距离、对话比例参考 |
| `pacing_profile` | 从 Reference Creation Profile 中 | 低 | 节奏感参考 |
| `chapter_structure_pattern` | 从 Reference Creation Profile 中 | 低 | 章节开篇/收尾风格参考 |
| `emotional_tone` | 从 Reference Creation Profile 中 | 低 | 情感基调参考 |
| `reader_hook_patterns` | 从 Reference Creation Profile 中 | 低 | 钩子策略参考 |

---

## 3. Daily Writer 不能读取或不能直接使用的内容

### 3.1 绝对禁止读取

| 内容 | 原因 |
|---|---|
| 参考小说原文（`raw_anonymous.txt`） | 会导致直接或间接复制原文 |
| 匿名化映射表（`name_map.json`） | 包含原始角色名和专有名词 |
| 参考小说原始文件 | 不经过分析抽象，直接读取违反原创原则 |
| 参考小说的分块文本（`chunks/`） | 过于具体，无法保证原创性 |

### 3.2 可存在于系统中但禁止 Daily Writer 读取

| 内容 | 禁止原因 |
|---|---|
| `character_archetypes`（Reference Creation Profile 中） | 人物原型是 Story Bible 生成阶段的参考，不是写作阶段的参考 |
| `conflict_patterns` | 冲突模式已在 Story Bible 生成时转化为原创剧情线 |
| `plot_progression_model` | 剧情模型已转化为 Story Bible 的 plot_threads |
| `worldbuilding_pattern` | 世界观已在 Story Bible 中设计完毕 |

---

## 4. Reference Creation Profile 在章节生成中的作用

Reference Creation Profile 在 Daily Writer 阶段的作用是**辅助性的风格参考**，而非**内容来源**。

```
Story Bible（内容来源，最高优先级）
    │
    ├── 角色 X 在当前章节应该做什么  →  来自 plot_threads
    ├── 角色 X 的说话方式            →  来自 characters
    ├── 当前场景应该在哪里            →  来自 locations
    └── 不允许违反的世界规则          →  来自 world_rules
    │
    ▼
Reference Creation Profile（风格参考，辅助性）
    │
    ├── 建议的叙事基调                →  来自 writing_style_profile
    ├── 建议的章节开篇方式            →  来自 chapter_structure_pattern
    └── 建议的情感底色                →  来自 emotional_tone
    │
    ▼
已有章节（上下文，连续性来源）
    │
    ├── 上一章结束时的角色状态
    ├── 上一章未解决的冲突
    └── 文风一致性检查
```

---

## 5. Story Bible 在章节生成中的优先级

| 决策维度 | 优先级顺序 |
|---|---|
| 角色行为 | Story Bible > Reference Creation Profile > 自由发挥 |
| 场景选择 | Story Bible > 已有章节线索 > Reference Creation Profile |
| 剧情推进 | Story Bible plot_threads > 已有章节 > 本章目标 |
| 文风语调 | Story Bible style > Reference Creation Profile writing_style_profile > 已有章节文风 |
| 冲突设计 | Story Bible > plot_threads > Reference Creation Profile conflict_patterns（间接） |

当 Story Bible 的约束与 Reference Creation Profile 的建议发生冲突时，**Story Bible 优先**。

---

## 6. Daily Writer 的输入顺序

Daily Writer 在构造 AI 生成 prompt 时，应按照以下顺序组织输入：

```
1. System Prompt（固定的生成约束）
   ├── "你是 NovelMind 平台的小说章节生成器"
   ├── "你的任务是生成用户自己的原创小说章节"
   ├── "你不是续写别人小说的工具"
   └── "你必须严格遵循 Story Bible 中的设定"

2. Story Bible 摘要（内容约束）
   ├── 本章涉及的角色及其当前状态
   ├── 本章涉及的地点
   ├── 本章要推进的剧情线
   └── 本章适用的世界规则

3. 本章写作目标
   ├── 本章标题/编号
   ├── 目标字数
   └── 本章在剧情线中的位置

4. 已有章节摘要（连续性约束）
   ├── 上一章摘要（关键事件、角色状态、未完冲突）
   └── 更早章节的必要上下文

5. 风格参考（可选，来自 Reference Creation Profile）
   ├── 建议的叙事基调
   ├── 建议的章节开篇/收尾风格
   └── 建议的情感底色

6. 生成约束
   ├── "不要生成任何涉及参考小说的内容"
   ├── "不要提及任何参考小说中的角色名、地名"
   └── "不要照搬任何已有章节的表达方式"
```

---

## 7. Daily Writer 的禁止事项

### 7.1 关于参考小说的禁止事项

| 禁止行为 | 严重程度 | 检测方式 |
|---|---|---|
| 直接续写参考小说 | critical | Originality Checker 扫描 |
| 以参考小说原文作为章节生成输入 | critical | 输入审查 |
| 在章节中提到参考小说的角色名 | critical | Originality Checker 扫描 |
| 在章节中引用参考小说的原文段落 | critical | Originality Checker 扫描 |
| 复刻参考小说的剧情桥段 | critical | Plot Reskin Checker 扫描 |
| 在 prompt 中加入参考小说原文 | critical | 输入审查 |
| 在 prompt 中描述"请模仿参考小说的 XX 桥段" | critical | 输入审查 |

### 7.2 关于章节安全的硬性规则（已有规则重申）

| 规则 | 来源 |
|---|---|
| 不能覆盖已有章节文件 | TASK-002 起 |
| 写入前必须检查目标路径是否存在 | DEVELOPMENT_RULES.md |
| 如果目标文件存在，必须失败 | DEVELOPMENT_RULES.md |
| 不允许使用 `-Force` 覆盖 | DEVELOPMENT_RULES.md |

---

## 8. prompt 组装规则

### 8.1 章节生成 prompt 必须包含

- System Prompt 中的身份声明："你是 NovelMind 平台的原创小说章节生成器"
- Story Bible 中与本章相关的角色、地点、剧情线设定
- 上一章的简要摘要（不超过 500 字）
- 本章目标描述（不超过 200 字）
- 原创性声明："本章生成内容必须是用户原创小说的延续，不得包含任何参考小说中的元素"

### 8.2 章节生成 prompt 不能包含

- 参考小说的任何原文
- 参考小说的角色名、地名、专有名词（即使已匿名化）
- "请模仿参考小说的风格" 或类似指令
- "请延续参考小说的剧情" 或类似指令
- `name_map.json` 中的任何内容

### 8.3 Reference Creation Profile 参与 prompt 的方式

仅以下字段可通过风格约束的方式出现在 prompt 中：

```
风格约束（来自 Reference Creation Profile，可选）：
- 叙事基调：冷峻克制，避免直白抒情
- 对话比例：约 30% 对话，70% 叙述
- 句法风格：中短句为主，节奏干净
- 章节开篇：以场景描写或人物状态开章
- 章节收尾：以情感余韵收尾
```

这些约束应以**通用风格指导**的形式呈现，不应提及"参考小说"或任何具体作品信息。

---

## 9. 和 backend/ai/gateway.py 的关系

```
Daily Writer
    │
    ├── 组装章节生成 prompt
    │     ├── 从 Story Bible 提取内容约束
    │     ├── 从已有章节提取上下文
    │     ├── 从 Reference Creation Profile 提取风格约束
    │     └── 组装为完整的 AI 请求
    │
    ▼
backend/ai/gateway.py
    │  唯一 AI 调用入口
    │
    ▼
AI Provider（通过 gateway 调用）
    │
    ▼
返回章节内容
    │
    ▼
Originality Checker（章节生成后检查）
    │
    ▼
写入 novels/{project_id}/chapters/{chapter_id}.md
```

严禁 Daily Writer 绕过 `backend/ai/gateway.py` 直接调用 AI Provider。

---

## 10. 和 prompts/reference_novel_analysis_prompt.md 的关系

两个 prompt 是不同阶段的独立 prompt，服务于不同目标：

| | reference_novel_analysis_prompt | Daily Writer 章节生成 prompt |
|---|---|---|
| 阶段 | 参考小说分析阶段 | 章节生成阶段 |
| 输入 | 参考小说分块文本 + 摘要 | Story Bible + 已有章节 + 风格参考 |
| 输出 | Reference Creation Profile | 原创小说章节 |
| 是否涉及参考小说 | 是（已匿名化） | 否 |
| 是否可读取 Reference Creation Profile | 不适用（它自己就是输出） | 是（仅风格字段） |
| 是否可读取参考小说原文 | 是（已匿名化） | 否 |
| AI 调用方式 | 通过 gateway | 通过 gateway |

**它们是同一链路上的不同环节，不互相调用，不互相包含。**

---

## 11. 后续 Claude Code 实现任务拆分

| 子任务 | 范围 | 建议负责人 |
|---|---|---|
| T066-IMPL-01 | 实现 Daily Writer 输入组装器（按优先级顺序组装 prompt） | Claude Code |
| T066-IMPL-02 | 实现输入安全审查（禁止读取参考小说原文） | Claude Code |
| T066-IMPL-03 | 实现风格约束注入器（从 Reference Creation Profile 提取风格字段） | Claude Code |
| T066-IMPL-04 | 实现章节生成 prompt 模板 | Codex |
| T066-IMPL-05 | 实现生成后 Originality Checker 集成 | Claude Code |
| T066-IMPL-06 | 实现章节写入安全逻辑（不覆盖、不修改） | Claude Code |
| T066-IMPL-07 | 添加 Daily Writer 安全检查到 `verify-all.ps1` | Codex |

---

## 12. 版本记录

| 版本 | 日期 | 变更说明 |
|---|---|---|
| 0.1.0 | 2026-05-24 | 初始草案，覆盖读取边界、输入顺序、禁止事项和实现拆分 |
