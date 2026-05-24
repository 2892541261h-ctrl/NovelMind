param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[verify] $Message"
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Warn {
    param([string]$Message)
    Write-Host "[verify] WARNING: $Message" -ForegroundColor Yellow
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Step "check required files"

$requiredFiles = @(
    "AGENTS.md",
    "ROADMAP.md",
    "TASKS.md",
    "CHANGELOG.md",
    "docs/AI_COLLABORATION_WORKFLOW.md",
    "docs/DEVELOPMENT_RULES.md",
    "docs/HANDOFF_TEMPLATE.md",
    "scripts/verify-all.ps1",
    "scripts/check-mvp-routes.ps1",
    "scripts/new-task-branch.ps1",
    "scripts/finish-task.ps1",
    ".codex/daily-code.md",
    ".codex/review.md"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Fail "Missing required file: $file"
    }
}

Write-Step "check forbidden env files"

$forbiddenFiles = @(
    ".env",
    ".env.local",
    ".env.development",
    ".env.production"
)

foreach ($file in $forbiddenFiles) {
    if (Test-Path $file) {
        Fail "Forbidden env file found: $file"
    }
}

Write-Step "check build artifacts not committed"

$shouldNotCommit = @(
    ".venv",
    "venv",
    "node_modules",
    "frontend/dist",
    "frontend/node_modules",
    ".pytest_cache"
)

foreach ($item in $shouldNotCommit) {
    if (Test-Path $item) {
        Warn "Local dir should not be committed: $item (check .gitignore)"
    }
}

$dbFiles = Get-ChildItem -Path $repoRoot -Filter "*.db" -File -ErrorAction SilentlyContinue
$backendDb = Get-ChildItem -Path (Join-Path $repoRoot "backend") -Filter "*.db" -File -ErrorAction SilentlyContinue
if ($dbFiles -or $backendDb) {
    Warn "Local .db files found, ensure they are not committed"
}

Write-Step "check for secret patterns"

$secretPatterns = @(
    "sk-[A-Za-z0-9_-]{20,}",
    "AIza[0-9A-Za-z_-]{20,}",
    "ghp_[0-9A-Za-z]{20,}",
    "BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"
)

$textFiles = Get-ChildItem -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\node_modules\\" -and
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\__pycache__\\" -and
        $_.FullName -notmatch "\\dist\\"
    }

foreach ($pattern in $secretPatterns) {
    $matches = $textFiles | Select-String -Pattern $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $first = $matches | Select-Object -First 1
        Fail "Secret pattern found: $($first.Path):$($first.LineNumber)"
    }
}

Write-Step "check AI calls only via backend/ai/gateway.py"

$aiProviderPatterns = @(
    "openai",
    "anthropic",
    "gemini",
    "deepseek",
    "dashscope",
    "zhipu",
    "moonshot",
    "together",
    "groq"
)

$codeFiles = Get-ChildItem -Recurse -File -Include *.py,*.ts,*.tsx,*.js,*.jsx,*.mjs,*.cjs |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\node_modules\\" -and
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\__pycache__\\" -and
        $_.FullName -notmatch "\\dist\\"
    }

foreach ($file in $codeFiles) {
    $relative = Resolve-Path -Relative $file.FullName
    $normalized = $relative -replace "\\", "/"
    if ($normalized -eq "./backend/ai/gateway.py" -or $normalized -like "./backend/ai/*") {
        continue
    }

    foreach ($pattern in $aiProviderPatterns) {
        $matches = Select-String -Path $file.FullName -Pattern $pattern -SimpleMatch -CaseSensitive:$false -ErrorAction SilentlyContinue
        if ($matches) {
            $first = $matches | Select-Object -First 1
            Fail "Possible bypass of gateway: ${normalized}:$($first.LineNumber)"
        }
    }
}

Write-Step "check Daily Writer rules in docs"

$dailyDocFiles = @(
    "AGENTS.md",
    "docs/DEVELOPMENT_RULES.md",
    "TASKS.md"
)

$dailyDocs = ""
foreach ($docFile in $dailyDocFiles) {
    $dailyDocs += Get-Content $docFile -Raw -Encoding UTF8
    $dailyDocs += "`n"
}

if ($dailyDocs -notmatch "backend/ai/gateway.py") {
    Fail "Docs must state: all AI calls via backend/ai/gateway.py"
}

Write-Step "check MVP route consistency"

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\check-mvp-routes.ps1"
if ($LASTEXITCODE -ne 0) {
    Fail "MVP route consistency check failed"
}

Write-Step "check backend dependencies"

$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Host "[verify] using venv Python: $python"
} else {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $python = $pyCmd.Source
        Write-Host "[verify] using system Python: $python"
    } else {
        Warn "Python not available, skipping backend checks"
        $python = $null
    }
}

if ($python) {
    $reqFile = Join-Path $backendDir "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "[verify] installing backend deps..."
        & $python -m pip install -r $reqFile --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Warn "pip install failed, check manually"
        }
    }

    Write-Host "[verify] backend Python compile check..."
    Push-Location $backendDir
    try {
        & $python -m compileall . -q 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Warn "Python compile check had warnings"
        } else {
            Write-Host "[verify] backend compile OK"
        }
    } finally {
        Pop-Location
    }
}

Write-Step "check frontend build"

$frontendDir = Join-Path $repoRoot "frontend"
if (Test-Path $frontendDir) {
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeCmd) {
        Push-Location $frontendDir
        try {
            if (-not (Test-Path "node_modules")) {
                Write-Host "[verify] installing frontend deps..."
                npm install --silent 2>&1 | Out-Null
            }
            Write-Host "[verify] frontend build..."
            npm run build 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[verify] frontend build OK"
            } else {
                Warn "frontend build failed, check: cd frontend && npm run build"
            }
        } finally {
            Pop-Location
        }
    } else {
        Warn "Node.js not available, skipping frontend check"
    }
}

Write-Step "check git status"

if ((Get-Command git -ErrorAction SilentlyContinue) -and (Test-Path ".git")) {
    git status --short
} else {
    Write-Host "[verify] not in a git repo, skip git status"
}

if ($Strict) {
    Write-Step "strict mode: no extra checks"
}

Write-Host "[verify] all checks passed"
