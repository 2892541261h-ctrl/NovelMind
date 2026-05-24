# 长文本分章与分块理解流程

> 版本：0.1.0
> 状态：草案（尚未实现）
> 关联任务：T063

---

## 1. 为什么长篇小说需要分章、分块理解

长篇小说（通常 5 万字以上）无法在单次 AI 调用中被完整理解：

- **上下文窗口限制：** 主流 AI 模型的上下文窗口有限，超过窗口的输入会被截断，导致遗漏关键信息
- **注意力衰减：** 即使技术上限允许超长输入，模型对长文本中部和尾部的注意力会下降
- **成本控制：** 单次超长输入消耗 token 极大，分块分析渐进投入更经济
- **分析精度：** 分块分析可以在每块中聚焦细节，通过累积摘要保持全书视角

**核心原则：** 分块是为了"逐段理解细节 → 跨块关联 → 全书级抽象"，不是简单切碎。

---

## 2. 总体分块流程

```
匿名化后的参考小说全文（raw_anonymous.txt）
    │
    ▼
第一遍：章节识别
    │  ├── 检测章节边界（# 标题、Chapter N、第 N 章 等）
    │  ├── 如果无章节标记，按自然段落 + 长度切分
    │  └── 生成章节映射表
    │
    ▼
第二遍：块切分
    │  ├── 每章按字数切分为 1-N 个分块
    │  ├── 每块控制在 3000-6000 字
    │  └── 块之间保留 200 字重叠（防止边界信息丢失）
    │
    ▼
第三遍：逐块分析（通过 AI Gateway）
    │  对每个块：
    │  ├── 输入：chunk_content + chunk_summary_{n-1} + accumulated_analysis
    │  ├── 调用 prompts/reference_novel_analysis_prompt.md
    │  └── 输出：更新后的 accumulated_analysis
    │
    ▼
第四遍：全书汇总
    │  ├── 输入：全部 accumulated_analysis
    │  ├── 调用 prompts/reference_novel_analysis_prompt.md（最终汇总模板）
    │  └── 输出：Reference Creation Profile
    │
    ▼
保存产物
    ├── novels/{project_id}/_reference/chunks/  ← 分块文件
    ├── novels/{project_id}/_reference/chunk_summaries/  ← 分块摘要
    ├── novels/{project_id}/_reference/accumulated_analysis.json  ← 累积分析
    └── novels/{project_id}/_reference/reference_creation_profile.json  ← 最终档案
```

---

## 3. 分章策略

### 3.1 章节边界检测

按优先级尝试以下模式：

| 优先级 | 检测模式 | 正则/规则 |
|---|---|---|
| 1 | Markdown 标题 | `^#+\s+.*`（一级或二级标题） |
| 2 | 英文章节 | `(?i)^Chapter\s+\d+` |
| 3 | 中文章节 | `第[零一二三四五六七八九十百千\d]+[章节回卷]` |
| 4 | 数字编号 | `^\d+[\.\、\s]+` |
| 5 | 分割线 | `^[\-\*=_]{3,}$` |
| 6 | 无标记 | 按 5000 字为一段落切分 |

### 3.2 章节数据结构

```json
{
  "chapter_index": 1,
  "title": "第一章",
  "start_offset": 0,
  "end_offset": 8532,
  "char_count": 8532,
  "detection_method": "chinese_chapter"
}
```

### 3.3 章节映射表

生成 `chapters_manifest.json`，记录全部章节的边界信息。

---

## 4. 分块策略

### 4.1 分块参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `chunk_size` | 4500 字 | 每块目标字数 |
| `chunk_min` | 2000 字 | 最小块大小（低于则不切分） |
| `chunk_max` | 6000 字 | 最大块大小（超过则切分） |
| `overlap` | 200 字 | 块间重叠字数（防止边界信息丢失） |

### 4.2 切分规则

1. **优先在自然段落边界切分**，不在句子中间切断
2. **块间重叠 200 字**，确保跨越切分点的信息不丢失
3. **每章超过 `chunk_max` 时才切分**，短章保持完整
4. **一章的最后一块**如果不足 `chunk_min`，合并到上一块

### 4.3 分块文件结构

```
novels/{project_id}/_reference/chunks/
├── 001_01.txt        ← 第 1 章第 1 块
├── 001_02.txt        ← 第 1 章第 2 块
├── 002_01.txt        ← 第 2 章第 1 块
└── ...
```

---

## 5. chunk_id 命名规则

**格式：** `{chapter_number:03d}_{chunk_number:02d}`

| 示例 | 含义 |
|---|---|
| `001_01` | 第 1 章第 1 块 |
| `003_02` | 第 3 章第 2 块 |
| `012_01` | 第 12 章第 1 块 |

对于无章节结构的文本，使用 `000_` 前缀：`000_01`、`000_02`...

**文件名：** `{chunk_id}.txt`

---

## 6. chunk_summary 生成规则

### 6.1 摘要内容

每个分块分析完成后，生成 `chunk_summary`，包含：

| 字段 | 说明 |
|---|---|
| `chunk_id` | 分块 ID |
| `chapter_range` | 覆盖的章节范围 |
| `key_events` | 关键事件列表（抽象描述，不抄原文） |
| `characters_introduced` | 本块中新引入的人物原型 |
| `worldbuilding_added` | 本块中新增的世界观信息 |
| `conflicts_identified` | 本块中出现的冲突模式 |
| `style_observations` | 本块中的文风观察 |
| `hooks_identified` | 本块中出现的读者钩子模式 |

### 6.2 摘要示例

```json
{
  "chunk_id": "001_01",
  "chapter_range": "第 1 章（前 4500 字）",
  "key_events": [
    "主角日常生活的场景建立 —— 工作场所、居住环境、通勤方式",
    "主角与同事的对话揭示职场氛围和人际关系",
    "主角与家人的远程通话暗示代际压力"
  ],
  "characters_introduced": [
    "主角：都市职业人原型，表面适应环境但内心有未表达的焦虑",
    "同事：务实、世俗化，作为主角的对照存在"
  ],
  "worldbuilding_added": [
    "故事设定在现实都市环境，无架空要素",
    "社会运行遵循现实逻辑：租房、加班、家庭期待"
  ],
  "conflicts_identified": [
    "主角内在：个人理想与现实压力的冲突（萌芽阶段）",
    "主角 vs 家庭期望：代际价值观差异"
  ],
  "style_observations": [
    "冷峻克制的叙述基调",
    "近距第三人称，跟随主角感知"
  ],
  "hooks_identified": [
    "人物共情：通过细腻的日常描写建立读者对主角的认同"
  ]
}
```

---

## 7. accumulated_analysis 增量分析规则

### 7.1 数据结构

```json
{
  "reference_title": "参考作品 A",
  "total_chunks": 24,
  "analyzed_chunks": 5,
  "last_chunk_id": "003_01",
  "profile_draft": {
    "genre": "...",
    "worldbuilding_pattern": "...",
    "character_archetypes": [...],
    "...": "..."
  },
  "cross_chunk_observations": [
    "第 1-3 章中出现的配角 X 原型在第 5 章被进一步验证",
    "冲突模式 A 在第 2 章和第 4 章以不同形式重复出现"
  ],
  "missing_dimensions": [
    "power_system_or_core_mechanism",
    "plot_progression_model"
  ]
}
```

### 7.2 增量更新规则

每次分析新的分块时：

1. **验证已有分析** — 新内容是否验证或挑战了之前的分析？更新对应字段和 confidence
2. **补充新维度** — 新内容覆盖了之前未分析的维度？补充到 `profile_draft`
3. **记录跨块关联** — 发现跨越多个分块的模式？记录到 `cross_chunk_observations`
4. **更新 missing_dimensions** — 哪些维度仍未被覆盖？保持追踪
5. **保留版本历史** — 每次更新保存一个快照，便于回溯

### 7.3 快照版本命名

```
novels/{project_id}/_reference/accumulated_analysis_snapshots/
├── snapshot_001.json    ← 分析第 1 块后
├── snapshot_005.json    ← 分析第 5 块后
├── snapshot_010.json    ← 分析第 10 块后
└── ...
```

---

## 8. 最终汇总为 Reference Creation Profile 的规则

全部块分析完成后，使用 `prompts/reference_novel_analysis_prompt.md` 中的"最终汇总模板"，输出完整的 `reference_creation_profile.json`。

汇总时应确保：

1. **全局视角** — 综合全部块的观察，而非单块视角的简单拼接
2. **去重合并** — 跨块重复出现的模式合并为一条
3. **confidence 综合评估** — 基于全部块的覆盖度评估置信度
4. **warnings 复核** — 最终检查是否有过度贴近参考小说的风险
5. **输出对齐** — JSON 字段严格对齐 `docs/REFERENCE_CREATION_PROFILE_SPEC.md`

---

## 9. 如何避免丢失长篇线索

| 问题 | 解决方案 |
|---|---|
| 前文铺垫在后文才揭示 | `cross_chunk_observations` 记录跨块模式，汇总时回溯关联 |
| 角色弧光跨越多个章节 | 每次分析时更新 `character_archetypes` 中的 `arc_type` 和 confidence |
| 伏笔在后续章节回收 | `accumulated_analysis` 中的 `cross_chunk_observations` 追踪伏笔 |
| 碎片化的世界观揭示 | 逐步累积到 `worldbuilding_pattern`，汇总时形成完整图景 |
| 多条剧情线交织 | 每条剧情线单独以 `plot_thread_id` 追踪，在 `plot_progression_model` 中整合 |

---

## 10. 如何避免模型直接复述原文

### 10.1 输入层面

- 匿名化预处理已移除角色名、地名和专有名词
- 分块文本已经过占位符替换，降低模型"引用原文"的可行性
- User Prompt 中强调"只能抽象规律"

### 10.2 Prompt 层面

- System Prompt 明确禁止复制原文
- 输出格式要求 JSON，而非自然语言叙述
- `chunk_summary` 要求抽象事件而非描述具体情节

### 10.3 输出层面

- 输出 JSON 的字段设计本身就是抽象层（规律、模式、原型），而非叙述层
- 后续 Originality Checker 会扫描输出中是否包含原文片段

---

## 11. 如何与 prompts/reference_novel_analysis_prompt.md 配合

| 分块阶段 | 使用的 Prompt 模板 | 输入 | 输出 |
|---|---|---|---|
| 首个分块 | 首次调用模板 | chunk_content + chunk_summary | accumulated_analysis（初始） |
| 中间分块 | 增量分析模板 | chunk_content + previous accumulated_analysis | updated accumulated_analysis |
| 最后分块 | 增量分析模板 | chunk_content + near-final accumulated_analysis | accumulated_analysis（最终） |
| 全书汇总 | 最终汇总模板 | accumulated_analysis（全部） | Reference Creation Profile |

本流程文档定义"何时"调用、"如何切分"和"如何累积"；Prompt 文档定义"调用时说什么"和"输出什么格式"。

---

## 12. 后续 Claude Code 实现任务拆分

| 子任务 | 范围 | 建议负责人 |
|---|---|---|
| T063-IMPL-01 | 实现章节边界检测器 | Claude Code |
| T063-IMPL-02 | 实现智能分块器（基于字数和段落边界） | Claude Code |
| T063-IMPL-03 | 实现 chunk_summary 生成器（调用 AI Gateway） | Claude Code |
| T063-IMPL-04 | 实现 accumulated_analysis 增量更新逻辑 | Claude Code |
| T063-IMPL-05 | 实现跨块关联追踪（cross_chunk_observations） | Claude Code |
| T063-IMPL-06 | 实现全书汇总流程 | Claude Code |
| T063-IMPL-07 | 创建分块文件管理 API | Claude Code |
| T063-IMPL-08 | 添加分块检查到 `verify-all.ps1` | Codex |

---

## 13. 版本记录

| 版本 | 日期 | 变更说明 |
|---|---|---|
| 0.1.0 | 2026-05-24 | 初始草案，覆盖分章、分块、摘要、增量分析和汇总流程 |
