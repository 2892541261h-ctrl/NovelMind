# 参考小说分析 Prompt 草案

> 版本：0.1.0
> 状态：草案（尚未接入 AI Gateway）
> 关联任务：T064

---

## 1. Prompt 名称

`reference_novel_analysis` — 参考小说创作方向分析

## 2. 使用场景

此 Prompt 用于 AI 阅读理解参考小说后，提取抽象创作规律，生成 Reference Creation Profile（参考创作档案）。

**工作流位置：**

```
参考小说原文（分块输入）
    │
    ▼
本 Prompt（reference_novel_analysis）
    │  → AI 分析抽象
    ▼
Reference Creation Profile（参考创作档案）
    │
    ▼
用户确认
    │
    ▼
Story Bible Generator（生成用户原创设定）
```

**调用方：** 后续将通过 `backend/ai/gateway.py` 调用。

**不用于：**
- 续写参考小说
- 改写参考小说
- 复制参考小说原文
- 生成参考小说的衍生内容

---

## 3. 输入变量说明

| 变量名 | 类型 | 说明 |
|---|---|---|
| `{{chunk_index}}` | `int` | 当前分块编号（从 1 开始） |
| `{{total_chunks}}` | `int` | 总分块数 |
| `{{chunk_content}}` | `string` | 当前分块的参考小说原文（已匿名化处理） |
| `{{chunk_summary}}` | `string` | 当前分块的情节摘要 |
| `{{accumulated_analysis}}` | `string \| null` | 已累积的分析结果（首次调用为 null） |
| `{{user_target_direction}}` | `string` | 用户目标创作方向描述 |
| `{{reference_title_anonymized}}` | `string` | 匿名化后的参考作品标题（例如"参考作品 A"） |

---

## 4. System Prompt 草案

```
你是 NovelMind 平台的参考小说分析器。你的唯一任务是：
从参考小说中提取抽象创作规律，生成 Reference Creation Profile。

# 核心身份
你不是续写作家，不是同人作者，不是翻译者。你是一个创作规律分析师。

# 允许做的事
- 抽象设定逻辑（例如："这个世界的力量体系基于等价交换原则"）
- 抽象人物类型（例如："主角属于反抗型成长原型，起始于被动接受环境的普通人"）
- 抽象剧情模式（例如："冲突以内心矛盾为主，外在事件是内心矛盾的外化"）
- 抽象文风特征（例如："冷峻克制，近距第三人称，对话约占 30%"）
- 抽象节奏规律（例如："慢热型，约每 8-10 章出现一次较大转折"）
- 抽象读者钩子模式（例如："依赖人物共情推动阅读，而非情节悬念"）

# 禁止做的事
- 不能复制参考小说原文段落（包括超过 15 个字词的连续引用）
- 不能搬运参考小说角色名（包括外号、代号、昵称）
- 不能搬运参考小说专有名词（包括地名、组织名、特殊物品名、招式名）
- 不能搬运参考小说完整剧情桥段（包括发生顺序、因果链条、场景组合）
- 不能对参考小说进行换皮（只改名字不改结构）
- 不能生成会让读者合理地认为是在续写参考小说的内容
- 不能以"举例"为名夹带参考小说原文

# 抽象原则
- 将"哈利·波特收到霍格沃茨录取通知书"抽象为"主角从平凡环境被引入隐藏的特殊世界"
- 将"鸣人的影分身之术"抽象为"主角拥有制造替身的能力"
- 将"路飞组建海贼团"抽象为"主角带领一个由不同特长成员组成的小团队"
- 将"死亡笔记的规则"抽象为"存在一种具有严格使用规则的超自然工具"

# 分析范围
依次从以下维度分析参考小说：
1. 世界观构建模式 —— 如何向读者揭示世界规则
2. 设定规则体系 —— 世界运行的底层逻辑
3. 力量体系/核心机制 —— 如果存在特殊体系，其抽象运作机制
4. 人物原型 —— 主要角色的原型、动机和成长弧
5. 关系模式 —— 人物之间关系的动态和张力的抽象模式
6. 冲突模式 —— 冲突类型、本质和典型解决方式
7. 剧情推进模型 —— 事件驱动还是人物驱动，线性还是非线性
8. 章节结构规律 —— 典型开篇方式、收尾方式、场景数
9. 写作风格特征 —— 基调、叙事距离、句法、对话比例
10. 叙事节奏 —— 快慢交替模式、事件密度
11. 情感基调 —— 整体情感底色
12. 读者钩子模式 —— 让读者持续阅读的机制
13. 应避免的方向 —— 从参考小说中识别的应规避陷阱
14. 原创性保障 —— 具体边界规则
15. 目标方向 —— 基于分析建议的原创方向

# 输出格式
你必须只输出一个合法的 JSON 对象。不要输出任何 JSON 之外的文字。
JSON 必须严格遵循 Reference Creation Profile 的字段规格。
```

---

## 5. User Prompt 模板

### 5.1 首次调用模板

```
== 分析任务 ==

你正在分析一部参考小说，用于帮助用户创建自己的原创小说。

== 参考信息 ==
- 匿名化标题：{{reference_title_anonymized}}
- 用户目标创作方向：{{user_target_direction}}

== 当前进度 ==
- 当前分块：{{chunk_index}} / {{total_chunks}}
- 已有累计分析：无（首次分析）

== 本块内容摘要 ==
{{chunk_summary}}

== 本块原文（已匿名化） ==
{{chunk_content}}

== 指令 ==
请基于以上内容，提取抽象创作规律，输出 Reference Creation Profile 的 JSON 草稿。
首次分析时，对于本块未覆盖到的维度，使用合理的 null 或空值填充，并在 missing_information 中标注。
```

### 5.2 增量分析模板（非首次调用）

```
== 分析任务 ==

你正在继续分析一部参考小说，用于帮助用户创建自己的原创小说。

== 参考信息 ==
- 匿名化标题：{{reference_title_anonymized}}
- 用户目标创作方向：{{user_target_direction}}

== 当前进度 ==
- 当前分块：{{chunk_index}} / {{total_chunks}}
- 已有累计分析：
{{accumulated_analysis}}

== 本块内容摘要 ==
{{chunk_summary}}

== 本块原文（已匿名化） ==
{{chunk_content}}

== 指令 ==
请在上一次累计分析的基础上，更新和补充 Reference Creation Profile。
- 如果新内容验证了已有分析，保持已有内容并适当提高 confidence。
- 如果新内容修正了已有分析，更新对应字段。
- 如果新内容覆盖了之前未覆盖的维度，补充对应字段。
- 在 missing_information 中更新仍缺失的维度列表。
- 如果发现任何维度存在过度贴近参考小说的风险，在 warnings 中标注。
```

### 5.3 最终汇总模板

```
== 分析任务 ==

你已完成对参考小说的全部 {{total_chunks}} 个分块的逐块分析。

== 参考信息 ==
- 匿名化标题：{{reference_title_anonymized}}
- 用户目标创作方向：{{user_target_direction}}

== 全部累计分析 ==
{{accumulated_analysis}}

== 指令 ==
请基于全部累计分析结果，生成最终的、完整的 Reference Creation Profile。
- 合并和去重所有分析内容。
- 对于所有字段给出最终版本。
- 综合评估整体 confidence。
- 检查是否有任何内容过度贴近参考小说，在 warnings 中标注。
- 在 target_novel_direction 中给出清晰、可操作的原创创作方向建议。
```

---

## 6. 输出 JSON 格式

### 完整字段描述

| JSON 字段 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `reference_title` | 参考作品标题 | `string` | 是 | 使用匿名化标题 |
| `genre` | 类型/流派 | `string` | 是 | 抽象流派组合 |
| `worldbuilding_pattern` | 世界观构建模式 | `string` | 是 | 如何向读者揭示世界规则 |
| `setting_rules` | 设定规则 | `list[string]` | 否 | 世界运行的底层逻辑 |
| `power_system_or_core_mechanism` | 力量体系/核心机制 | `string` | 否 | 特殊体系的抽象描述 |
| `character_archetypes` | 人物原型 | `list[object]` | 是 | 角色原型、动机、成长弧 |
| `relationship_patterns` | 关系模式 | `list[object]` | 否 | 人物关系动态和张力 |
| `conflict_patterns` | 冲突模式 | `list[object]` | 是 | 冲突类型、本质、解决方式 |
| `plot_progression_model` | 剧情推进模型 | `string` | 是 | 事件驱动还是人物驱动 |
| `chapter_structure_pattern` | 章节结构规律 | `object` | 否 | 开篇/收尾方式、场景数 |
| `writing_style_profile` | 写作风格档案 | `object` | 是 | 基调、叙事距离、句法 |
| `pacing_profile` | 节奏档案 | `object` | 否 | 快慢交替、事件密度 |
| `emotional_tone` | 情感基调 | `string` | 否 | 整体情感底色 |
| `reader_hook_patterns` | 读者钩子模式 | `list[string]` | 否 | 持续阅读的动力机制 |
| `taboo_or_avoid_rules` | 禁忌/避免规则 | `list[string]` | 否 | 应规避的陷阱 |
| `originality_rules` | 原创性规则 | `list[object]` | 是 | 生成时的原创性约束 |
| `target_novel_direction` | 目标小说方向 | `string` | 是 | 基于分析建议的原创方向 |
| `confidence` | 分析置信度 | `object` | 是 | 各维度置信度评估 |
| `missing_information` | 缺失信息 | `list[string]` | 是 | 还缺哪些参考内容 |
| `warnings` | 风险警告 | `list[object]` | 是 | 过度贴近参考小说的风险 |

### `confidence` 对象结构

```json
{
  "overall": "high | medium | low",
  "by_field": {
    "genre": "high",
    "worldbuilding_pattern": "medium",
    "character_archetypes": "high",
    "...": "..."
  }
}
```

### `warnings` 项结构

```json
{
  "type": "string（too_similar / potential_copy / naming_risk / plot_resemblance）",
  "field": "string（关联字段名）",
  "detail": "string（风险描述）",
  "severity": "critical | high | medium | low"
}
```

---

## 7. 字段对齐说明

以上 20 个输出字段与 `docs/REFERENCE_CREATION_PROFILE_SPEC.md` 定义的 17 个核心字段严格对齐，并增加 3 个过程字段：

- `confidence` — 过程字段，记录 AI 对各维度分析的置信度
- `missing_information` — 过程字段，标注分析中尚未覆盖的维度
- `warnings` — 过程字段，标注过度贴近参考小说的风险

过程字段在后续生成用户原创 Story Bible 时可被消费，但不写入最终的 Story Bible 设定文件中。

---

## 8. 原创性约束

### 8.1 System Prompt 层面的约束

System Prompt 已经内置以下约束，AI 必须遵守：

1. **不复制原文** — 不得输出任何超过 15 字词的参考小说原文连续片段
2. **不搬运名称** — 不得输出参考小说中的角色名、地名、组织名、专有名词
3. **不搬运桥段** — 不得输出可识别的具体剧情桥段或情节链条
4. **不换皮** — 不得仅在名词层面替换后复刻人物关系网络或剧情结构
5. **不暗示续写** — 不得生成会让读者误以为是在续写参考小说的内容

### 8.2 输出层面的约束

`originality_rules` 字段必须包含至少 3 条具体可执行的原创性规则，每条规则需说明：

- 规则内容（`rule`）
- 严重程度（`severity`：critical / high / medium / low）
- 违规时的动作（`action_on_violation`：阻止生成 / 标记高风险 / 标记警告）

### 8.3 warnings 字段的使用

AI 在分析过程中如发现以下情况，必须在 `warnings` 中标注：

- 分析结果中的某些描述可以直接对应回参考小说原文
- 某些抽象规律过于具体（实际上在描述参考小说的独有特征）
- 输出的人物关系网络与参考小说高度同构
- 对力量体系的抽象实际上是在描述参考小说独有的体系

---

## 9. 安全失败策略

### 9.1 输入层面的安全检查

在调用 AI 之前，系统应执行以下检查（后续实现，当前阶段只定义策略）：

1. **分块内容检查：** 确保分块内容已经过匿名化处理（参考小说中的角色名/地名/专有名词已被替换为占位符）
2. **输入大小检查：** 确保单次调用的 `chunk_content` 不超过模型上下文窗口的 70%（预留空间给 System Prompt 和 User Prompt 模板）
3. **格式检查：** 确保输入为 UTF-8 编码的纯文本

### 9.2 输出层面的安全检查

AI 返回 JSON 后，系统应执行以下检查：

1. **JSON 合法性：** 检查返回内容是否为合法 JSON
2. **字段完备性：** 检查必填字段是否存在
3. **原创性扫描：** 检查输出内容中是否包含疑似参考小说原文的字符串
4. **名称扫描：** 检查输出中是否包含已知的参考小说角色名、地名、专有名词
5. **warnings 复核：** 如果 `warnings` 中存在 `severity: critical` 的条目，流程必须暂停并转入人工确认

### 9.3 失败处理

| 失败类型 | 处理方式 |
|---|---|
| JSON 不合法 | 记录错误日志，重试 1 次。仍失败则终止并报告 |
| 必填字段缺失 | 记录缺失字段，重试时在 User Prompt 中补充缺失字段的明确要求。仍缺失则标记 `missing_information` |
| 检测到原文复制 | 终止分析，标记为 `severity: critical`，转入人工审查 |
| 检测到名称搬运 | 终止分析，标记为 `severity: critical`，转入人工审查 |
| confidence 过低（overall: low） | 标记为需补充参考内容，不继续流向 Story Bible Generator |
| warnings 含 critical 条目 | 暂停流程，转入人工确认 |

---

## 10. 使用示例（最小输入/输出）

### 输入示例

```
== 分析任务 ==

你正在分析一部参考小说，用于帮助用户创建自己的原创小说。

== 参考信息 ==
- 匿名化标题：参考作品 A
- 用户目标创作方向：创作一部以当代中国二线城市为背景的都市现实主义长篇小说

== 当前进度 ==
- 当前分块：1 / 10
- 已有累计分析：无（首次分析）

== 本块内容摘要 ==
本章介绍了主角的日常生活：在一家广告公司工作，独自租住在城市北部的公寓。
描写了主角与同事的对话，以及深夜加班的场景。主角与母亲通电话时表现出对家庭期待的压力。

== 本块原文（已匿名化） ==
[已匿名化的分块文本内容...]

== 指令 ==
请基于以上内容，提取抽象创作规律，输出 Reference Creation Profile 的 JSON 草稿。
```

### 期望输出特征（非完整输出）

- `genre` 应包含"都市现实"
- `character_archetypes` 应抽象出主角的原型特征
- `conflict_patterns` 应识别"人物 vs 社会期望"的冲突模式
- `writing_style_profile` 应基于文本描述文风特征
- `confidence` 中未覆盖的维度应标注为 `low`
- `missing_information` 应列出尚未分析到的维度
- 输出中不应出现任何参考小说原文中的角色名、地名或专有名词

---

## 11. 版本记录

| 版本 | 日期 | 变更说明 |
|---|---|---|
| 0.1.0 | 2026-05-24 | 初始草案，覆盖 System Prompt、User Prompt 模板、输出格式、原创性约束和安全失败策略 |
