<#
.SYNOPSIS
  Build the NovelMind V1 Windows MSI installer preview.
.DESCRIPTION
  Runs the final release check first, then uses WiX Toolset when available.
  Build outputs are written to installer/dist and must not be committed.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$wxsPath = Join-Path $PSScriptRoot "NovelMind.wxs"
$distDir = Join-Path $PSScriptRoot "dist"
$msiPath = Join-Path $distDir "NovelMind-V1-Setup.msi"
$finalCheck = Join-Path $repoRoot "scripts\final-release-check.ps1"

function Find-CommandPath([string] $name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidatePaths = @(
        (Join-Path $env:USERPROFILE ".dotnet\tools\$name"),
        (Join-Path $env:ProgramFiles "WiX Toolset v4\bin\$name"),
        (Join-Path ${env:ProgramFiles(x86)} "WiX Toolset v4\bin\$name")
    )
    foreach ($candidate in $candidatePaths) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }

    return $null
}

Write-Host "[installer] running final release check..."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $finalCheck
if ($LASTEXITCODE -ne 0) {
    throw "final-release-check.ps1 failed; installer build stopped."
}

if (-not (Test-Path $wxsPath)) {
    throw "Missing WiX source file: $wxsPath"
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null

$wix = Find-CommandPath "wix.exe"
if ($wix) {
    Write-Host "[installer] using WiX CLI: $wix"
    & $wix build $wxsPath -d RepoRoot=$repoRoot -out $msiPath
    if ($LASTEXITCODE -ne 0) { throw "WiX build failed." }
    Write-Host "[installer] MSI generated: $msiPath"
    exit 0
}

Write-Host "[installer] WiX Toolset was not found." -ForegroundColor Yellow
Write-Host "[installer] Install WiX Toolset v4 (wix.exe), then rerun this script." -ForegroundColor Yellow
Write-Host "[installer] No MSI was generated." -ForegroundColor Yellow
exit 2
