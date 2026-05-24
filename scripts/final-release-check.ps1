<#
.SYNOPSIS
  Run NovelMind MVP 1.0 final local release checks.
#>

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[final-release] $Message"
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Invoke-CheckScript {
    param([string]$ScriptPath, [string]$Label)
    Write-Step "run $Label"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath
    if ($LASTEXITCODE -ne 0) {
        Fail "$Label failed"
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Step "start NovelMind MVP 1.0 final release check"

Invoke-CheckScript ".\scripts\check-env.ps1" "check-env.ps1"
Invoke-CheckScript ".\scripts\check-mvp-routes.ps1" "check-mvp-routes.ps1"
Invoke-CheckScript ".\scripts\verify-all.ps1" "verify-all.ps1"

Write-Step "check git working tree"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is unavailable"
}

$status = git status --short
if ($status) {
    Write-Host $status
    Fail "git status is not clean"
}

Write-Step "check forbidden tracked or staged files"

$trackedFiles = @(git ls-files)
$statusFiles = @()
git status --short | ForEach-Object {
    if ($_ -match "^...(.+)$") {
        $statusFiles += $Matches[1].Trim()
    }
}

$forbiddenPatterns = @(
    '(^|/)\.env$',
    '(^|/)\.env\.(local|development|production)$',
    '(^|/)\.venv/',
    '(^|/)venv/',
    '(^|/)node_modules/',
    '^frontend/node_modules/',
    '^frontend/dist/',
    '\.db$',
    '\.sqlite$',
    '\.sqlite3$',
    '\.log$',
    '\.tmp$'
)

foreach ($file in ($trackedFiles + $statusFiles)) {
    $normalized = $file -replace "\\", "/"
    foreach ($pattern in $forbiddenPatterns) {
        if ($normalized -match $pattern) {
            Fail "Forbidden file is tracked or pending commit: $normalized"
        }
    }
}

Write-Step "check local env and database files"

$localForbiddenFiles = @(
    ".env",
    ".env.local",
    ".env.development",
    ".env.production"
)

foreach ($file in $localForbiddenFiles) {
    if (Test-Path $file) {
        Fail "Forbidden local env file found: $file"
    }
}

$dbFiles = Get-ChildItem -Path $repoRoot -Recurse -File -Include *.db,*.sqlite,*.sqlite3 -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\node_modules\\"
    }

if ($dbFiles) {
    $firstDb = $dbFiles | Select-Object -First 1
    Fail "Local database file found: $($firstDb.FullName)"
}

Write-Step "check credential patterns"

$credentialPatterns = @(
    'sk-[A-Za-z0-9_-]{20,}',
    'AIza[0-9A-Za-z_-]{20,}',
    'ghp_[0-9A-Za-z]{20,}',
    'xox[baprs]-[A-Za-z0-9-]{20,}',
    'BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY'
)

$trackedTextFiles = $trackedFiles |
    Where-Object {
        $_ -match '\.(py|ps1|md|txt|json|toml|yaml|yml|ts|tsx|js|jsx|html|css)$' -and
        $_ -notmatch '(^|/)package-lock\.json$'
    }

foreach ($pattern in $credentialPatterns) {
    foreach ($file in $trackedTextFiles) {
        if (-not (Test-Path $file)) {
            continue
        }
        $matches = Select-String -Path $file -Pattern $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $first = $matches | Select-Object -First 1
            Fail "Credential-like pattern found: $($first.Path):$($first.LineNumber)"
        }
    }
}

Write-Step "check exported novel files"

$exportedNovelPattern = '^(exports|output|outputs|release|releases|novels)/.+\.(md|txt)$'
foreach ($file in ($trackedFiles + $statusFiles)) {
    $normalized = $file -replace "\\", "/"
    if ($normalized -match $exportedNovelPattern) {
        Fail "Exported novel file appears tracked or pending commit: $normalized"
    }
}

Write-Step "check large temporary files"

foreach ($file in $trackedFiles) {
    if (-not (Test-Path $file)) {
        continue
    }
    $item = Get-Item $file -ErrorAction SilentlyContinue
    if ($item -and $item.Length -gt 10MB) {
        Fail "Large tracked file found: $file"
    }
}

Write-Host "[final-release] MVP 1.0 final release check passed"
