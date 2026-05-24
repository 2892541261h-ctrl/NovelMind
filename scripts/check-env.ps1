<#
.SYNOPSIS
  Check NovelMind local dev environment.
#>

$ErrorActionPreference = "Continue"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Write-Check {
    param([string]$Label, [string]$Status, [string]$Color)
    Write-Host ("  {0,-35} " -f "$Label") -NoNewline
    Write-Host $Status -ForegroundColor $Color
}

Write-Host "`n=== NovelMind Environment Check ===`n"

# Git
Write-Host "[Git]"
$gitBranch = & git -C $repoRoot branch --show-current 2>$null
if ($gitBranch) {
    Write-Check "current branch" $gitBranch "Green"
} else {
    Write-Check "current branch" "unavailable" "Red"
}
$gitStatus = & git -C $repoRoot status --short 2>$null
if ($LASTEXITCODE -eq 0) {
    if ($gitStatus) {
        Write-Check "git status" "uncommitted changes" "Yellow"
    } else {
        Write-Check "git status" "clean" "Green"
    }
} else {
    Write-Check "git status" "unavailable" "Red"
}

# Python
Write-Host "`n[Python]"
$python = $null
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Check ".venv" "exists" "Green"
    $pyVer = & $python --version 2>&1
    Write-Check "Python version" $pyVer "Green"
} else {
    Write-Check ".venv" "not found" "Yellow"
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $python = $pyCmd.Source
        $pyVer = & python --version 2>&1
        Write-Check "Python (system)" $pyVer "Yellow"
    } else {
        Write-Check "Python" "unavailable" "Red"
    }
}

if ($python) {
    $pipOk = & $python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Check "pip" "available" "Green"
    } else {
        Write-Check "pip" "unavailable" "Red"
    }
}

$reqFile = Join-Path $repoRoot "backend\requirements.txt"
if (Test-Path $reqFile) {
    Write-Check "backend/requirements.txt" "exists" "Green"
} else {
    Write-Check "backend/requirements.txt" "missing" "Red"
}

# Node.js
Write-Host "`n[Node.js]"
$nodeVer = & node --version 2>$null
if ($nodeVer) {
    Write-Check "Node.js version" $nodeVer "Green"
} else {
    Write-Check "Node.js" "unavailable" "Red"
}

$npmVer = & npm --version 2>$null
if ($npmVer) {
    Write-Check "npm version" $npmVer "Green"
} else {
    Write-Check "npm" "unavailable" "Red"
}

$pkgFile = Join-Path $repoRoot "frontend\package.json"
if (Test-Path $pkgFile) {
    Write-Check "frontend/package.json" "exists" "Green"
} else {
    Write-Check "frontend/package.json" "missing" "Red"
}

$nodeModules = Join-Path $repoRoot "frontend\node_modules"
if (Test-Path $nodeModules) {
    Write-Check "node_modules" "installed" "Green"
} else {
    Write-Check "node_modules" "not installed" "Yellow"
}

# Safety
Write-Host "`n[Safety files]"
$envFile = Join-Path $repoRoot ".env"
if (Test-Path $envFile) {
    Write-Check ".env" "exists (do not commit)" "Yellow"
} else {
    Write-Check ".env" "absent" "Green"
}

Write-Host "`n=== Check complete ===`n"
