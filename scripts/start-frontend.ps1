<#
.SYNOPSIS
  启动 NovelMind 前端开发服务器。
.DESCRIPTION
  自动安装依赖并启动 Vite 开发服务器。
#>

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$frontendDir = Join-Path $repoRoot "frontend"

Write-Host "[frontend] 进入 $frontendDir"
Set-Location $frontendDir

if (-not (Test-Path "node_modules")) {
    Write-Host "[frontend] node_modules 不存在，正在安装依赖..."
    npm.cmd install
}

Write-Host "[frontend] 启动 Vite 开发服务器 (http://127.0.0.1:5173)"
npm.cmd run dev
