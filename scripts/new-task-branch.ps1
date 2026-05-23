param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^T[0-9]{3,}$")]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[a-z0-9][a-z0-9-]*$")]
    [string]$Slug
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 git。请先安装 Git for Windows，或在已配置 git 的 PowerShell 中运行。"
    exit 1
}

if (-not (Test-Path ".git")) {
    Write-Error "当前目录不是 Git 仓库，无法创建任务分支。"
    exit 1
}

$branchName = "task/$TaskId-$Slug"

Write-Host "[branch] 准备创建任务分支：$branchName"

$status = git status --short
if ($status) {
    Write-Host "[branch] 当前工作区存在未提交变更："
    $status
    Write-Error "请先提交、暂存或交接当前变更，再创建新任务分支。"
    exit 1
}

$existing = git branch --list $branchName
if ($existing) {
    Write-Error "分支已存在：$branchName"
    exit 1
}

git switch -c $branchName

Write-Host "[branch] 已切换到：$branchName"
Write-Host "[branch] 完成任务后运行：.\scripts\finish-task.ps1"



