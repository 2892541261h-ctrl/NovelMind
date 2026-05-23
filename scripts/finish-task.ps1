$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host "[finish] 运行统一检查"
& (Join-Path $PSScriptRoot "verify-all.ps1")

Write-Host "[finish] 检查 Git 状态"
if ((Get-Command git -ErrorAction SilentlyContinue) -and (Test-Path ".git")) {
    git status --short
    Write-Host "[finish] 请确认 TASKS.md 和 CHANGELOG.md 已按任务更新。"
    Write-Host "[finish] Pull Request 描述建议使用 docs/HANDOFF_TEMPLATE.md。"
} else {
    Write-Host "[finish] 当前不在 Git 仓库内，跳过 Git 状态检查。"
}

Write-Host "[finish] 收尾检查完成"



