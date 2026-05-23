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

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Step "检查必需文件"

$requiredFiles = @(
    "AGENTS.md",
    "ROADMAP.md",
    "TASKS.md",
    "CHANGELOG.md",
    "docs/AI_COLLABORATION_WORKFLOW.md",
    "docs/DEVELOPMENT_RULES.md",
    "docs/HANDOFF_TEMPLATE.md",
    "scripts/verify-all.ps1",
    "scripts/new-task-branch.ps1",
    "scripts/finish-task.ps1",
    ".codex/daily-code.md",
    ".codex/review.md"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Fail "缺少必需文件：$file"
    }
}

Write-Step "检查禁止提交的本地环境文件"

$forbiddenFiles = @(
    ".env",
    ".env.local",
    ".env.development",
    ".env.production"
)

foreach ($file in $forbiddenFiles) {
    if (Test-Path $file) {
        Fail "禁止提交或保留环境文件：$file"
    }
}

Write-Step "检查疑似密钥内容"

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
        $_.FullName -notmatch "\\__pycache__\\"
    }

foreach ($pattern in $secretPatterns) {
    $matches = $textFiles | Select-String -Pattern $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $first = $matches | Select-Object -First 1
        Fail "发现疑似密钥内容：$($first.Path):$($first.LineNumber)"
    }
}

Write-Step "检查 AI 调用必须通过 backend/ai/gateway.py"

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
        $_.FullName -notmatch "\\__pycache__\\"
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
            Fail "发现可能绕过 gateway 的 AI Provider 引用：${normalized}:$($first.LineNumber)"
        }
    }
}

Write-Step "检查 Daily Writer 规则文档"

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

if ($dailyDocs -notmatch "不能覆盖已有章节") {
    Fail "Daily Writer 文档必须明确：不能覆盖已有章节"
}

if ($dailyDocs -notmatch "backend/ai/gateway.py") {
    Fail "文档必须明确：所有 AI 调用只能通过 backend/ai/gateway.py"
}

Write-Step "检查 Git 状态"

if ((Get-Command git -ErrorAction SilentlyContinue) -and (Test-Path ".git")) {
    git status --short
} else {
    Write-Host "[verify] 当前不在 Git 仓库内，跳过 git status"
}

if ($Strict) {
    Write-Step "Strict 模式当前没有额外检查"
}

Write-Host "[verify] 全部检查通过"





