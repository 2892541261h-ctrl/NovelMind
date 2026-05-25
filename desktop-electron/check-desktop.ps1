<#
.SYNOPSIS
  Validate NovelMind Electron desktop environment.
.DESCRIPTION
  Checks that all prerequisites for building/running the Electron
  desktop client are in place. Does NOT build anything.
#>

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[check-desktop] $Message"
}

function Warn {
    param([string]$Message)
    Write-Host "[check-desktop] WARNING: $Message" -ForegroundColor Yellow
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$desktopDir = Join-Path $repoRoot "desktop-electron"

Write-Step "check Node.js"
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Fail "Node.js is not installed. Install Node.js 18+ from https://nodejs.org"
}
Write-Host "[check-desktop] Node.js: $($nodeCmd.Source)"

Write-Step "check npm"
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Fail "npm is not installed."
}
Write-Host "[check-desktop] npm: $($npmCmd.Source)"

Write-Step "check Python"
$repoVenvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pythonPath = $null
if (Test-Path $repoVenvPython) {
    $pythonPath = $repoVenvPython
    Write-Host "[check-desktop] Python (.venv): $pythonPath"
} else {
    $sysPython = Get-Command python -ErrorAction SilentlyContinue
    if ($sysPython) {
        $pythonPath = $sysPython.Source
        Write-Host "[check-desktop] Python (system): $pythonPath"
    } else {
        Warn "Python not found — backend will not start"
    }
}

Write-Step "check frontend build"
$distIndex = Join-Path $repoRoot "frontend\dist\index.html"
if (Test-Path $distIndex) {
    Write-Host "[check-desktop] frontend: built"
} else {
    Warn "frontend/dist/index.html not found. Run: cd frontend && npm run build"
}

Write-Step "check desktop-electron/ files"
$requiredDesktopFiles = @(
    "package.json",
    "main.js",
    "preload.js",
    "backend.js",
    "tray.js",
    "frontend-loader.js",
    "build.js",
    "assets/NovelMind.ico"
)

foreach ($file in $requiredDesktopFiles) {
    $fullPath = Join-Path $desktopDir $file
    if (-not (Test-Path $fullPath)) {
        Fail "Missing desktop file: $file"
    }
}
Write-Host "[check-desktop] all desktop files present"

Write-Step "check desktop-electron/node_modules"
$nodeModules = Join-Path $desktopDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Warn "desktop-electron/node_modules not installed. Run: cd desktop-electron && npm install"
} else {
    $electronPkg = Join-Path $nodeModules "electron\package.json"
    if (Test-Path $electronPkg) {
        $version = (Get-Content $electronPkg -Raw | ConvertFrom-Json).version
        Write-Host "[check-desktop] electron: v$version"
    } else {
        Warn "electron not installed in node_modules. Run: cd desktop-electron && npm install"
    }
}

Write-Step "check tray icon"
$trayIcon = Join-Path $desktopDir "assets\NovelMind.ico"
if (Test-Path $trayIcon) {
    Write-Host "[check-desktop] tray icon: OK ($trayIcon)"
} else {
    Warn "tray icon not found: $trayIcon"
}

Write-Step "check backend requirements.txt"
$reqFile = Join-Path $repoRoot "backend\requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "[check-desktop] backend requirements: OK"
} else {
    Fail "backend/requirements.txt not found"
}

Write-Host "[check-desktop] all checks passed"
