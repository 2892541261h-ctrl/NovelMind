# Windows Installer Preview Note

If the branch includes Windows installer work, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-installer.ps1` before pushing. Do not commit `installer/dist/`, `.msi`, `.exe`, `.zip`, `.wixobj`, or `.wixpdb` build artifacts. If an MSI is later published, upload it manually as a GitHub Release artifact after final checks; do not store installer binaries in Git.

# GitHub Upload Guide

本指南用于把本地 `main` 上传到 GitHub 前的人工确认。这里只写流程，不自动 push，不创建 tag，不连接 GitHub。

## 1. 确认当前在 main

```powershell
git branch --show-current
git status --short
```

预期：

- 当前分支是 `main`
- `git status --short` 无输出

## 2. 运行最终封版检查

上传前建议先确认 `docs/MVP_ACCEPTANCE_REPORT.md` 已生成，并且报告中的检查结果均为通过。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

预期：

- 输出 `MVP 1.0 final release check passed`
- 不创建 `.env`
- 不提交 `.venv`、`node_modules`、`frontend/dist` 或数据库文件

## 3. 查看本地领先远程的 commit

```powershell
git log --oneline origin/main..main
```

如果没有配置远程或远程为空仓库，先人工确认 remote：

```powershell
git remote -v
```

如果 remote 地址不符合预期，停止，不要覆盖。

## 4. 确认没有敏感文件

```powershell
git status --short
git ls-files | Select-String -Pattern "\.env$|\.db$|node_modules|frontend/dist|\.venv"
```

还需要人工确认：

- 没有 API Key、Token、Cookie、私钥或真实凭证。
- 没有导出的 Markdown / TXT 小说文件。
- 没有大型日志或临时文件。

## 5. 上传 main

确认以上全部通过后，才执行：

```powershell
git push origin main
```

如果认证失败，停止并处理 GitHub 登录问题。不要 force push。

## 6. 可选创建本地 tag

只有在人工确认需要打版本标记时才执行：

```powershell
git tag v1.0.0-mvp
```

## 7. 可选上传 tag

只有在人工确认 tag 正确后才执行：

```powershell
git push origin v1.0.0-mvp
```

## 8. 上传后检查

```powershell
git status --short
git log --oneline -5
```

确认：

- 工作区仍然 clean
- 最新 commit 与预期一致
- GitHub 页面可以看到最新内容
