# 从 Reference Creation Profile 生成原创 Story Bible 的流程

> 版本：0.1.0
> 状态：草案（尚未实现）
> 关联任务：T065

---

## 1. 功能定位

此流程是"参考小说驱动原创写作"链路中的核心转换环节：将抽象的 Reference Creation Profile（参考创作档案）转化为用户自己的原创 Story Bible（小说设定）。

**核心原则：**

```
Reference Creation Profile           Story Bible
（参考方向，来源于参考小说）          （原创设定，属于用户自己）
        │                                    │
        └──── 抽象规律指导原创设计 ────────────┘
```

**不是：** 将参考小说的角色改个名字、换个地点、调个能力体系就塞进 Story Bible。这是换皮，是禁止的。

**是：** 参考"该类作品常用什么样的冲突模式"和"角色的成长弧有哪几种典型"，然后设计出全新的角色、全新的世界观、全新的剧情线。

---

## 2. 总体流程

```
Reference Creation Profile（已确认）
    │  + 用户原创方向描述
    ▼
Story Bible Generator（通过 AI Gateway）
    │  ← 使用专用的 Story Bible Generation Prompt
    │  ← 输入：Reference Creation Profile 的抽象字段
    │  ← 输入：用户的原创方向描述
    │  ← 约束：原创性检查规则
    │
    ▼
StoryBible 草案（JSON）
    │
    ▼
Originality Checker（自动检查）
    │  ├── 检查是否搬运了参考小说角色名 → critical
    │  ├── 检查是否复刻了完整人物关系网络 → high
    │  ├── 检查是否换皮了剧情桥段 → high
    │  ├── 检查是否过度贴近参考小说 → medium
    │  └── 检查结果 → PASS / WARN / FAIL
    │
    ├── FAIL → 终止，返回修改建议
    ├── WARN → 标记，转入用户人工确认
    └── PASS ↓
    │
    ▼
用户确认 / 修改 / 拒绝
    │  ├── 确认 → 保存为正式 Story Bible
    │  ├── 修改 → 用户编辑后重新提交 Originality Checker
    │  └── 拒绝 → 回到 Story Bible Generator 重新生成
    │
    ▼
保存 StoryBible
    novels/{project_id}/story-bible.json
```

---

## 3. 输入与输出

### 3.1 输入

| 输入项 | 来源 | 说明 |
|---|---|---|
| Reference Creation Profile | `novels/{project_id}/_reference/reference_creation_profile.json` | 已由用户确认的参考创作档案 |
| 用户原创方向描述 | 用户输入（文本） | 用户对目标小说的总体设想 |
| 原创性检查规则 | 系统内置 + `originality_rules` 字段 | 从 Reference Creation Profile 中提取的原创性边界 |

### 3.2 输出

| 输出项 | 目标位置 | 说明 |
|---|---|---|
| StoryBible 草案 | 内存（暂不写入文件） | 完整的原创小说设定 |
| Originality Check 报告 | 返回给用户 | 检查通过/警告/失败详情 |
| 最终 StoryBible | `novels/{project_id}/story-bible.json` | 用户确认后写入 |

---

## 4. 必须明确的禁止事项

在生成 Story Bible 的过程中，AI 必须遵守以下禁止事项：

### 4.1 名称层面

| 禁止 | 允许 |
|---|---|
| 使用参考小说角色名 | 创造全新的原创角色名 |
| 使用参考小说地名 | 创造全新的原创地名 |
| 使用参考小说组织名/势力名 | 创造全新的原创组织名称 |
| 使用参考小说的专有术语 | 如需使用类型术语（如"修真""异能"），保持通用性 |

### 4.2 结构层面

| 禁止 | 允许 |
|---|---|
| 复制参考小说的人物关系网络（只改名字） | 设计全新的人物关系网络 |
| 复制参考小说的剧情链条（事件 A→B→C） | 设计全新的剧情推进逻辑 |
| 复制参考小说的力量体系（只改招式名） | 设计全新的力量体系（可借鉴抽象规律） |
| 复制参考小说的章节结构（每章对应同样事件类型） | 参考章节结构规律设计全新结构 |

### 4.3 内容层面

| 禁止 | 允许 |
|---|---|
| 搬运完整剧情桥段 | 抽象剧情模式后设计原创桥段 |
| 搬运超过 15 字词的连续原文 | 用自己的语言描述设定 |
| 生成"相当于参考小说的 XX 角色"的说明 | 独立描述每个角色的特质 |

---

## 5. 如何把参考创作档案转化为原创世界观

### 5.1 世界观转化步骤

```
Reference Creation Profile 提供：           StoryBible 产出：
┌─────────────────────────────┐           ┌─────────────────────────────┐
│ worldbuilding_pattern       │ ───→      │ 世界观揭示节奏设计          │
│ "逐步揭示型，随剧情展开"    │  借鉴规律  │ "第一章只展现代码世界，      │
│                             │           │  第三章才揭示底层架构"      │
├─────────────────────────────┤           ├─────────────────────────────┤
│ setting_rules               │ ───→      │ 原创世界规则                │
│ "现实逻辑，无超自然"        │  参考方向  │ "故事中的程序世界遵循       │
│                             │           │  严格的图灵完备逻辑"        │
├─────────────────────────────┤           ├─────────────────────────────┤
│ power_system_or_            │ ───→      │ 原创核心机制                │
│ core_mechanism              │  抽象借鉴  │ "程序员通过编写特定         │
│ "能力来源于训练和经验"      │           │  代码片段获得临时权限"      │
└─────────────────────────────┘           └─────────────────────────────┘
```

### 5.2 关键转化原则

1. **规律迁移，不照搬设定** — 从参考小说学到的是"现实逻辑的感觉很吸引读者"，而非"把现实世界复制过来"
2. **组合创新** — 从多部参考小说中学到的规律可以组合出全新的世界
3. **差异化参数** — 对每条抽象规律，至少在一个维度上做显式差异化

---

## 6. 如何生成原创角色

### 6.1 角色生成输入

从 Reference Creation Profile 中读取：

| 字段 | 用途 |
|---|---|
| `character_archetypes[].archetype` | 角色原型的抽象描述（如"反抗型成长主角"） |
| `character_archetypes[].core_motivation` | 角色的核心动机 |
| `character_archetypes[].arc_type` | 角色的成长弧类型 |
| `relationship_patterns[].dynamic` | 人物关系的动态模式 |
| `relationship_patterns[].tension_source` | 人物关系的张力来源 |

### 6.2 角色生成规则

1. **保留原型，替换具体** — 保留"反抗型成长主角"的原型，但创造全新的人物背景、职业、性格细节
2. **打散重组** — 不要 1:1 映射。参考小说有 5 个主要角色，原创小说可以有 3 个或 7 个
3. **关系模式可借鉴，关系网络必须全新** — "若即若离的恋人"是模式（允许），"大公司的总监和建筑师在同一栋楼工作"是具体（禁止照搬）
4. **角色名独立生成** — 使用全新的命名逻辑，不可通过同音字、形近字、翻译等变体照搬

---

## 7. 如何生成原创冲突

### 7.1 冲突生成输入

从 Reference Creation Profile 中读取：

| 字段 | 用途 |
|---|---|
| `conflict_patterns[].type` | 冲突类型（人物 vs 自我 / 人物 vs 社会 / 人物 vs 人物） |
| `conflict_patterns[].nature` | 冲突本质 |
| `conflict_patterns[].resolution_style` | 冲突解决方式 |

### 7.2 冲突生成规则

1. **保留冲突类型，创造全新冲突内容** — "人物 vs 自我"是类型（允许），"主角在广告行业感到倦怠"是具体（禁止照搬）
2. **冲突来源独立设计** — 参考小说中冲突来自"家庭催婚"，原创小说中冲突可以来自完全不同但同类型的社会压力
3. **冲突组合创新** — 可以将参考小说中不同类型的冲突重新组合

---

## 8. 如何生成原创剧情主线

### 8.1 剧情生成输入

从 Reference Creation Profile 中读取：

| 字段 | 用途 |
|---|---|
| `plot_progression_model` | 剧情推进模型 |
| `chapter_structure_pattern` | 章节结构规律 |
| `pacing_profile` | 叙事节奏 |
| `reader_hook_patterns` | 读者钩子模式 |

### 8.2 剧情生成规则

1. **借鉴推进模型，不搬运剧情链条** — "人物驱动 + 日常推进型"是模型（允许），"第 1 章上班、第 3 章相亲、第 5 章父亲生病"是链条（禁止）
2. **钩子模式可借鉴，具体钩子必须原创** — "人物共情型钩子"是模式（允许），"通过深夜加班场景建立共情"是具体设计（允许原创），"通过广告公司深夜加班建立共情"是照搬（禁止）
3. **严格避免剧情换皮** — 不能把参考小说的"主角在第 N 章遇到事件 X"换成"主角在第 N 章遇到事件 Y"但事件本质相同

---

## 9. 如何生成原创风格约束

### 9.1 风格生成输入

从 Reference Creation Profile 中读取：

| 字段 | 用途 |
|---|---|
| `writing_style_profile.tone` | 叙事基调 |
| `writing_style_profile.narration_distance` | 叙事距离 |
| `writing_style_profile.dialogue_ratio` | 对话比例 |
| `writing_style_profile.description_style` | 描写风格 |
| `writing_style_profile.sentence_style` | 句法特征 |
| `emotional_tone` | 情感基调 |

### 9.2 风格生成规则

1. **风格参数可直接作为约束** — "冷峻克制的叙事基调"可以直接写入 StyleProfile
2. **情感基调可迁移但需适配原创世界观** — 如果原创小说设定比参考小说更暗黑，情感基调也需要调整
3. **句法、对话比例等可以近似参考** — 这些是技术性参数，不同作品之间借鉴空间较大

---

## 10. 如何让 Daily Writer 使用生成后的 Story Bible

Story Bible 生成并确认后，写入 `novels/{project_id}/story-bible.json`，与 TASK-004 创建的 Story Bible API 完全兼容。

Daily Writer 的工作方式（T066 详细规划）：

```
StoryBible（用户原创设定）
    │
    ├── metadata        → 章节命名、目标字数
    ├── characters      → 角色行为约束
    ├── locations       → 场景选择
    ├── world_rules     → 世界观一致性约束
    ├── plot_threads    → 剧情线推进
    └── style           → 写作风格约束
    │
    ▼
Daily Writer → novels/{project_id}/chapters/{chapter_id}.md
```

Reference Creation Profile 在 Daily Writer 阶段仅作为**间接参考方向**，不直接作为生成输入。

---

## 11. 如何加入 Originality Checker

### 11.1 检查时机

| 检查点 | 时机 | 检查内容 |
|---|---|---|
| 生成后检查 | Story Bible 草案生成后 | 完整原创性扫描 |
| 用户修改后检查 | 用户编辑 Story Bible 后 | 重新扫描修改部分 |
| 章节生成后检查 | Daily Writer 每章生成后 | 检查章节是否过度贴近参考小说 |

### 11.2 检查维度

| 维度 | 检查方法 | 严重程度 |
|---|---|---|
| 角色名 | 对照 `name_map.json` 检查是否出现原始名称或变体 | critical |
| 地名/组织名 | 对照匿名化映射表检查 | critical |
| 人物关系网络 | 图结构相似度检查（结构同构度 > 80% → 高风险） | high |
| 剧情链条 | 事件序列相似度检查（连续 3 个以上事件同构 → 高风险） | high |
| 原文片段 | 字符串相似度（最长公共子序列 > 15 字词 → critical） | critical |
| 整体贴近度 | 多维度综合评分 | medium |

### 11.3 检查结果处理

| 结果 | 动作 |
|---|---|
| PASS（全部通过） | 允许继续 |
| WARN（存在 medium 级别告警） | 标记告警，建议人工审查，不阻止流程 |
| FAIL（存在 high 或 critical） | 阻止流程，返回具体问题和修改建议 |

---

## 12. 后续 Claude Code 实现任务拆分

| 子任务 | 范围 | 建议负责人 |
|---|---|---|
| T065-IMPL-01 | 设计 Story Bible Generation Prompt（AI 生成原创设定） | Codex |
| T065-IMPL-02 | 实现 Story Bible Generator 服务（调用 AI Gateway） | Claude Code |
| T065-IMPL-03 | 实现 Originality Checker 核心检查逻辑 | Claude Code |
| T065-IMPL-04 | 实现角色名/地名对照检查 | Claude Code |
| T065-IMPL-05 | 实现人物关系网络图结构相似度检查 | Claude Code |
| T065-IMPL-06 | 实现剧情链条相似度检查 | Claude Code |
| T065-IMPL-07 | 实现用户确认/修改/拒绝的交互流程 API | Claude Code |
| T065-IMPL-08 | 将 Originality Checker 集成到 Daily Writer 流程中 | Claude Code |
| T065-IMPL-09 | 添加原创性检查到 `verify-all.ps1` | Codex |

---

## 13. 版本记录

| 版本 | 日期 | 变更说明 |
|---|---|---|
| 0.1.0 | 2026-05-24 | 初始草案，覆盖生成流程、禁止事项、各方转化规则和 Originality Checker 集成 |
