<#
.SYNOPSIS
  Launch NovelMind local services and open the web UI.
.DESCRIPTION
  This launcher is intended for the Windows installer preview. It reuses the
  existing local development startup script and does not create .env files or
  store API keys.
#>

$ErrorActionPreference = "Stop"

try {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
    $startDevScript = Join-Path $PSScriptRoot "start-dev.ps1"

    if (-not (Test-Path $startDevScript)) {
        throw "Missing startup script: $startDevScript"
    }

    Write-Host "NovelMind V1 local launcher"
    Write-Host "Backend:  http://localhost:8000"
    Write-Host "Frontend: http://localhost:5173"
    Write-Host ""
    Write-Host "Starting local backend and frontend windows..."

    Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$startDevScript`"" `
        -WorkingDirectory $repoRoot

    Write-Host "Waiting briefly before opening the browser..."
    Start-Sleep -Seconds 6

    Write-Host "Opening http://localhost:5173"
    Start-Process "http://localhost:5173"

    Write-Host ""
    Write-Host "If the page is not ready yet, wait for the backend/frontend windows to finish starting and refresh the browser."
    Write-Host "Press Enter to close this launcher window. Closing this window will not stop the service windows."
    Read-Host | Out-Null
}
catch {
    Write-Host ""
    Write-Host "NovelMind failed to start." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Press Enter to close this window."
    Read-Host | Out-Null
    exit 1
}
