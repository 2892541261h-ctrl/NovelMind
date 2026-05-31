<#
.SYNOPSIS
  启动 NovelMind 后端开发服务器。
.DESCRIPTION
  优先使用项目 .venv，自动安装依赖，启动 FastAPI + uvicorn。
#>

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendDir = Join-Path $repoRoot "backend"

Write-Host "[backend] 进入 $backendDir"
Set-Location $backendDir

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "[backend] 使用虚拟环境: $venvPython"
    $python = $venvPython
    $pip = Join-Path $repoRoot ".venv\Scripts\pip.exe"
} else {
    Write-Host "[backend] .venv 不存在，请先创建虚拟环境："
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "如果 python 指向 WindowsApps 占位符，请先关闭应用执行别名："
    Write-Host "  Windows 设置 -> 应用 -> 应用执行别名 -> 关闭 python.exe 和 python3.exe"
    exit 1
}

Write-Host "[backend] 安装依赖..."
& $python -m pip install -r requirements.txt --quiet 2>&1 | Out-Null

Write-Host "[backend] 启动 FastAPI 开发服务器 (http://127.0.0.1:8765)"
& $python -m uvicorn main:app --reload --host 127.0.0.1 --port 8765
