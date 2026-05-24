<#
.SYNOPSIS
  一键启动 NovelMind 后端和前端开发服务器。
.DESCRIPTION
  分别在两个 PowerShell 窗口中启动后端和前端。
#>

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendScript = Join-Path $PSScriptRoot "start-backend.ps1"
$frontendScript = Join-Path $PSScriptRoot "start-frontend.ps1"

Write-Host "[dev] 启动后端..."
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$backendScript`"" -WorkingDirectory $repoRoot

Write-Host "[dev] 启动前端..."
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$frontendScript`"" -WorkingDirectory $repoRoot

Write-Host "[dev] 后端: http://127.0.0.1:8000"
Write-Host "[dev] 前端: http://127.0.0.1:5173"
Write-Host "[dev] 健康检查: Invoke-RestMethod http://127.0.0.1:8000/health"
