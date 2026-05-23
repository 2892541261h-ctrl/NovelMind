# Codex 代码审查提示词

用于 NovelMind 项目的代码审查。

## 审查重点

优先找问题，不先写总结。按严重程度排序：

- 是否提交了 API Key、Token、Cookie、私钥或 `.env`。
- 是否绕过 `backend/ai/gateway.py` 直接调用 AI Provider。
- Daily Writer 是否可能覆盖已有章节。
- GitHub Actions 是否可能泄露密钥或提交异常文件。
- 任务是否超出 `TASKS.md` 范围。
- 是否引入未讨论的依赖。
- Windows PowerShell 命令是否可用。
- 是否缺少必要检查。

## AI 调用审查规则

任何 AI Provider 调用都必须经过：

```text
backend/ai/gateway.py
```

需要重点搜索：

- `openai`
- `anthropic`
- `gemini`
- `deepseek`
- `dashscope`
- `zhipu`
- `moonshot`
- `together`
- `groq`

如果这些引用出现在 `backend/ai/` 之外，需要要求修改或解释。

## Daily Writer 审查规则

必须确认：

- 写章节前检查目标文件是否存在。
- 目标文件存在时失败。
- 不使用 `-Force` 覆盖章节。
- 不清空章节目录。
- 不修改已发布章节正文。

## 输出格式

如果发现问题：

```text
发现问题：

1. [严重程度] 文件:行号 - 问题说明

建议：

- 修改建议
```

如果没有发现问题：

```text
没有发现必须阻塞的问题。

剩余风险：

- 说明未覆盖的检查范围
```
