# 参考小说导入流程

> 版本：0.1.0
> 状态：草案（尚未实现）
> 关联任务：T062

---

## 1. 功能定位

参考小说导入流程是"参考小说驱动原创写作"功能链路的第一个环节。其唯一目的将用户提供的参考小说安全地引入系统，供后续 AI 分析抽象使用。

**核心约束：**

| 允许 | 禁止 |
|---|---|
| 读取参考小说文本，用于后续分析 | 将参考小说直接作为 Daily Writer 输入 |
| 提取创作规律和抽象模式 | 保存参考小说到章节输出目录 |
| 生成匿名化的中间分析产物 | 在公开 PR 中包含参考小说原文 |
| 在本地工作区临时存储 | 将参考小说上传到公开 GitHub 仓库 |

---

## 2. 总体导入流程

```
用户选择参考小说文件
    │
    ▼
文件安全校验
    │  ├── 文件大小检查
    │  ├── 编码格式检查
    │  ├── 文件类型检查
    │  └── 重复导入检查
    │
    ▼
文本提取 & 规范化
    │  ├── 多格式文本提取（.txt / .md / .docx / .epub）
    │  └── 统一为 UTF-8 纯文本
    │
    ▼
匿名化预处理（可选，建议）
    │  ├── 替换已知角色名 → [角色A]、[角色B]
    │  ├── 替换已知地名   → [地点1]、[地点2]
    │  └── 保留可恢复映射表（仅本地，不提交）
    │
    ▼
保存到本地工作目录
    │  novels/{project_id}/_reference/
    │  ├── raw_anonymous.txt       ← 匿名化后的全文
    │  ├── import_manifest.json    ← 导入元数据
    │  └── name_map.json           ← 匿名化映射表（不提交 Git）
    │
    ▼
触发后续流程
    ├── T063：长文本分章分块
    └── T064：AI 分析生成 Reference Creation Profile
```

---

## 3. 支持的输入形式规划

当前为规划阶段，不实现具体解析器。后续由 Claude Code 实现。

| 格式 | 扩展名 | 优先级 | 解析策略 | 实现状态 |
|---|---|---|---|---|
| 纯文本 | `.txt` | P0 | 直接读取，自动检测编码 | 规划中 |
| Markdown | `.md` | P0 | 直接读取，UTF-8 | 规划中 |
| Word 文档 | `.docx` | P1 | 使用 `python-docx` 提取纯文本 | 规划中 |
| 电子书 | `.epub` | P1 | 使用 `ebooklib` 提取纯文本 | 规划中 |
| PDF | `.pdf` | P2 | 使用 `pymupdf` 或 `pdfplumber` 提取 | 待评估 |

**输入大小分级：**

| 级别 | 字数范围 | 处理策略 |
|---|---|---|
| 短篇 | < 5 万字 | 单次分块分析（≤ 10 个块） |
| 中篇 | 5-20 万字 | 多次分块分析（10-20 个块） |
| 长篇 | 20-80 万字 | 多次分块分析 + 全书级汇总 |
| 超长篇 | > 80 万字 | 警告用户，建议选择代表性卷/篇章 |

---

## 4. 文件安全规则

### 4.1 大小限制

- 单文件最大 100 MB（超过此限制拒绝导入）
- 解析后的纯文本最大 200 万字（超过截断并警告）

### 4.2 编码处理

- 优先尝试 UTF-8
- 失败则尝试 UTF-16、GBK、Shift-JIS
- 所有格式最终统一转为 UTF-8

### 4.3 内容类型验证

- 拒绝非文本文件（二进制、图片、视频、压缩包）
- 对于 .docx 和 .epub，先验证文件头魔数
- 拒绝被加密或 DRM 保护的文件

### 4.4 文件散列

- 导入时计算文件的 SHA-256 散列
- 记录在 `import_manifest.json` 中
- 同一项目若已导入相同散列文件，提示用户"已存在相同文件，是否覆盖？"

---

## 5. 参考小说存储与隔离规则

### 5.1 本地存储结构

```
novels/{project_id}/_reference/
├── raw_anonymous.txt        ← 匿名化后的参考小说全文（UTF-8）
├── import_manifest.json     ← 导入元数据
└── name_map.json            ← 匿名化映射表（.gitignore 排除）
```

### 5.2 Git 管理规则

| 文件 | 是否提交 Git | 说明 |
|---|---|---|
| `raw_anonymous.txt` | 是（已匿名化） | 匿名化后不包含原始专有名词 |
| `import_manifest.json` | 是 | 包含文件名、散列、导入时间、字数等元数据 |
| `name_map.json` | **绝不提交** | 包含原始名称到匿名化名称的映射，列入 `.gitignore` |
| 原始参考小说文件 | **绝不提交** | 用户提供的原始文件不得进入 Git 仓库 |

### 5.3 公开输出隔离

- 所有自动生成的 Pull Request 不得包含参考小说原文
- 所有自动生成的 Pull Request 不得包含 `name_map.json`
- 所有自动生成的 Pull Request 只能包含匿名化后的分析产物
- `novels/{project_id}/_reference/` 目录整体在 PR 中仅包含匿名化产物

---

## 6. 导入后生成的中间产物

| 产物 | 生成时机 | 说明 |
|---|---|---|
| `import_manifest.json` | 导入完成 | 记录文件名、散列、字数、导入时间、编码、原始格式 |
| `raw_anonymous.txt` | 匿名化后 | 匿名化处理后的全文，供分块使用 |
| `name_map.json` | 匿名化时 | 原始名称到占位符的映射（仅本地） |
| `chunks/` 目录 | T063 分块 | 分块后的文本片段和摘要 |
| `accumulated_analysis.json` | AI 分析中 | 增量累积的分析结果 |
| `reference_creation_profile.json` | AI 分析完成后 | 最终 Reference Creation Profile |

---

## 7. 导入失败处理

| 失败场景 | 错误码 | 处理方式 |
|---|---|---|
| 文件不存在 | `FILE_NOT_FOUND` | 返回 422，提示用户检查路径 |
| 文件过大（> 100 MB） | `FILE_TOO_LARGE` | 返回 413，提示大小限制 |
| 不支持的文件格式 | `UNSUPPORTED_FORMAT` | 返回 415，列出支持的格式 |
| 文件为二进制/非文本 | `NON_TEXT_CONTENT` | 返回 415，提示提供文本格式 |
| 文件加密/DRM 保护 | `DRM_PROTECTED` | 返回 422，提示解除保护 |
| 编码检测失败 | `ENCODING_ERROR` | 返回 422，提示提供 UTF-8 编码版本 |
| 解析后文本为空 | `EMPTY_CONTENT` | 返回 422，提示检查文件内容 |
| 重复导入（相同 SHA-256） | `DUPLICATE_IMPORT` | 返回 409，提示已存在，询问是否覆盖 |
| 解析后字数过少（< 1000 字） | `CONTENT_TOO_SHORT` | 返回 422，提示参考小说内容不足 |

---

## 8. Windows 本地开发注意事项

- 文件路径使用 `pathlib.Path`，避免硬编码 `\` 或 `/`
- 编码检测优先使用 `chardet` 库（纯 Python，跨平台）
- 大文件读取使用流式处理，避免一次性加载到内存
- `.docx` 和 `.epub` 的解析库（`python-docx`、`ebooklib`）均为纯 Python，Windows 兼容
- 匿名化映射表使用 JSON 格式，本地编码为 UTF-8
- 所有文件操作使用 `encoding="utf-8"` 显式指定

---

## 9. 后续 Claude Code 实现任务拆分

T062 规划完成后，后续实现任务建议拆分为：

| 子任务 | 范围 | 建议负责人 |
|---|---|---|
| T062-IMPL-01 | 实现文件安全校验模块（大小、类型、编码检测） | Claude Code |
| T062-IMPL-02 | 实现 .txt/.md 文本提取器 | Claude Code |
| T062-IMPL-03 | 实现 .docx 文本提取器（引入 `python-docx`） | Claude Code |
| T062-IMPL-04 | 实现 .epub 文本提取器（引入 `ebooklib`） | Claude Code |
| T062-IMPL-05 | 实现导入清单 `import_manifest.json` 生成逻辑 | Claude Code |
| T062-IMPL-06 | 实现匿名化预处理流水线 | Claude Code |
| T062-IMPL-07 | 创建 `novels/{project_id}/_reference/` API 端点 | Claude Code |
| T062-IMPL-08 | 更新 `.gitignore` 排除 `name_map.json` | Codex |
| T062-IMPL-09 | 添加导入安全校验到 `verify-all.ps1` | Codex |

---

## 10. 版本记录

| 版本 | 日期 | 变更说明 |
|---|---|---|
| 0.1.0 | 2026-05-24 | 初始草案，覆盖导入流程、输入格式、安全规则、失败处理和实现拆分 |
