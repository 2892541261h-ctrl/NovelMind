<#
.SYNOPSIS
  Check NovelMind Windows installer preview files and safety rules.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Fail([string] $message) {
    Write-Host "[installer-check] FAIL: $message" -ForegroundColor Red
    exit 1
}

function Pass([string] $message) {
    Write-Host "[installer-check] $message"
}

function Require-File([string] $relativePath) {
    $path = Join-Path $repoRoot $relativePath
    if (-not (Test-Path $path)) {
        Fail "missing required file: $relativePath"
    }
    Pass "found $relativePath"
}

Push-Location $repoRoot
try {
    Require-File "NovelMind Launcher.bat"
    Require-File "scripts\launch-novelmind.ps1"
    Require-File "scripts\check-installer.ps1"
    Require-File "installer\build-msi.ps1"
    Require-File "installer\README.md"
    Require-File "installer\NovelMind.wxs"
    Require-File "installer\assets\NovelMind.ico"
    Require-File "docs\WINDOWS_INSTALLER_GUIDE.md"

    $wxs = Get-Content "installer\NovelMind.wxs" -Raw
    if ($wxs -notmatch 'NovelMind\.ico') {
        Fail "NovelMind.wxs does not reference NovelMind.ico"
    }
    if ($wxs -notmatch 'Icon="NovelMindIcon"') {
        Fail "NovelMind shortcuts do not use NovelMindIcon"
    }
    if ($wxs -notmatch 'ARPPRODUCTICON') {
        Fail "NovelMind.wxs does not configure ARPPRODUCTICON"
    }
    Pass "WiX icon configuration is present"

    $gitignore = Get-Content ".gitignore" -Raw
    $requiredIgnores = @(
        "installer/dist/",
        "*.msi",
        "*.wixpdb",
        "*.wixobj",
        "installer/**/*.msi",
        "installer/**/*.exe",
        "installer/**/*.zip"
    )
    foreach ($rule in $requiredIgnores) {
        if ($gitignore -notmatch [regex]::Escape($rule)) {
            Fail ".gitignore missing installer artifact rule: $rule"
        }
    }
    Pass ".gitignore includes installer artifact rules"

    $trackedBinaries = git ls-files | Select-String -Pattern '\.(msi|exe|zip)$'
    if ($trackedBinaries) {
        Fail "tracked installer binary artifacts found: $($trackedBinaries -join ', ')"
    }

    $statusBinaries = git status --short --untracked-files=all | Select-String -Pattern '\.(msi|exe|zip)$'
    if ($statusBinaries) {
        Fail "pending installer binary artifacts found: $($statusBinaries -join ', ')"
    }

    Pass "no MSI/EXE/ZIP artifacts are tracked or pending"
    Pass "installer preview checks passed"
}
finally {
    Pop-Location
}
