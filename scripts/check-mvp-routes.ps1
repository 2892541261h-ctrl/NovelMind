<#
.SYNOPSIS
  Check NovelMind MVP route and safety invariants before release.
#>

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[mvp-routes] $Message"
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Read-Text {
    param([string]$Path)
    return Get-Content $Path -Raw -Encoding UTF8
}

function Require-File {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        Fail "Missing required file: $Path"
    }
}

function Require-Text {
    param([string]$Path, [string]$Pattern, [string]$Label)
    $content = Read-Text $Path
    if ($content -notmatch [regex]::Escape($Pattern)) {
        Fail "$Label not found in $Path"
    }
}

function Reject-Text {
    param([string]$Path, [string]$Pattern, [string]$Label)
    $content = Read-Text $Path
    if ($content -match [regex]::Escape($Pattern)) {
        Fail "$Label found in $Path"
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Step "check key files"

$requiredFiles = @(
    "backend/main.py",
    "backend/routers/daily_writer.py",
    "backend/routers/formal_chapters.py",
    "backend/routers/exports.py",
    "backend/routers/reference_novels.py",
    "backend/services/daily_writer_service.py",
    "backend/services/chapter_draft_service.py",
    "backend/services/formal_chapter_service.py",
    "backend/services/export_service.py",
    "backend/services/reference_novel_service.py",
    "backend/schemas/chapter_draft.py",
    "backend/schemas/formal_chapter.py",
    "backend/schemas/writer_context.py",
    "frontend/src/pages/DailyWriterPage.tsx"
)

foreach ($file in $requiredFiles) {
    Require-File $file
}

Write-Step "check formal chapter API prefix"

Require-Text "backend/routers/formal_chapters.py" 'prefix="/api/formal-chapters"' "Formal chapter router prefix"
Reject-Text "backend/routers/formal_chapters.py" 'prefix="/api/chapters"' "Conflicting formal chapter router prefix"

Write-Step "check frontend API paths"

Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/daily-writer/generate" "Daily Writer generate API"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/daily-writer/chapters" "Daily Writer draft API"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/formal-chapters?project_id=" "Formal chapter list API"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/formal-chapters/publish-draft/" "Formal chapter publish API"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/formal-chapters/" "Formal chapter detail API"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/exports/project/" "Export API"
Reject-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/chapters/publish-draft/" "Old publish API path"
Reject-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/chapters?project_id=" "Old formal chapter list API path"

Write-Step "check AI Gateway and originality rules"

Require-Text "backend/services/chapter_draft_service.py" "from ai.gateway import generate_text" "Daily Writer AI Gateway import"
Require-Text "backend/services/chapter_draft_service.py" "generate_text(ai_req)" "Daily Writer AI Gateway call"
Require-Text "backend/services/reference_novel_service.py" "from ai.gateway import generate_text" "Reference analysis AI Gateway import"
Require-Text "backend/services/reference_novel_service.py" "generate_text(request)" "Reference analysis AI Gateway call"
Require-Text "backend/services/daily_writer_service.py" "get_latest_profile_for_project" "Reference Profile context lookup"
Require-Text "backend/services/daily_writer_service.py" "DO NOT continue or extend any reference novel." "No continuation rule"
Require-Text "backend/services/daily_writer_service.py" "DO NOT copy original text from any reference work." "No copy rule"
Require-Text "backend/services/daily_writer_service.py" "DO NOT reuse character names, place names, organization names, or plot events from reference works." "No specific entity reuse rule"
Require-Text "backend/services/daily_writer_service.py" "ONLY abstract narrative rhythm, conflict patterns, worldbuilding approaches, character relationship structures, and writing style direction." "Abstract-only rule"
Require-Text "backend/services/daily_writer_service.py" "ALL generated content MUST serve the user's own original novel." "Original novel rule"

Write-Step "check runtime route table"

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Fail "Python unavailable; cannot import backend route table"
    }
    $python = $pythonCmd.Source
}

$routeCheck = @'
import importlib
import sys

sys.path.insert(0, "backend")

modules = [
    "routers.daily_writer",
    "routers.formal_chapters",
    "routers.exports",
    "routers.reference_novels",
    "services.daily_writer_service",
    "services.chapter_draft_service",
    "services.formal_chapter_service",
    "services.export_service",
    "services.reference_novel_service",
    "schemas.chapter_draft",
    "schemas.formal_chapter",
    "schemas.writer_context",
]

for module_name in modules:
    importlib.import_module(module_name)

from main import app

routes = []
for route in app.routes:
    path = getattr(route, "path", "")
    methods = set(getattr(route, "methods", []) or [])
    endpoint = getattr(route, "endpoint", None)
    module = getattr(endpoint, "__module__", "")
    routes.append((path, methods, module))

def require(path, method, module_prefix):
    for route_path, route_methods, route_module in routes:
        if route_path == path and method in route_methods and route_module.startswith(module_prefix):
            return
    raise SystemExit(f"Missing route: {method} {path} from {module_prefix}")

require("/api/daily-writer/generate", "POST", "routers.daily_writer")
require("/api/daily-writer/chapters", "GET", "routers.daily_writer")
require("/api/daily-writer/chapters/{draft_id}", "GET", "routers.daily_writer")
require("/api/daily-writer/chapters/{draft_id}", "PATCH", "routers.daily_writer")
require("/api/daily-writer/chapters/{draft_id}", "DELETE", "routers.daily_writer")
require("/api/formal-chapters", "GET", "routers.formal_chapters")
require("/api/formal-chapters/{chapter_id}", "GET", "routers.formal_chapters")
require("/api/formal-chapters/{chapter_id}", "PATCH", "routers.formal_chapters")
require("/api/formal-chapters/{chapter_id}", "DELETE", "routers.formal_chapters")
require("/api/formal-chapters/publish-draft/{draft_id}", "POST", "routers.formal_chapters")
require("/api/exports/project/{project_id}/markdown", "GET", "routers.exports")
require("/api/exports/project/{project_id}/txt", "GET", "routers.exports")
require("/api/reference-novels", "GET", "routers.reference_novels")
require("/api/reference-novels/{novel_id}/analyze", "POST", "routers.reference_novels")

for route_path, _, route_module in routes:
    if route_path.startswith("/api/chapters") and route_module.startswith("routers.formal_chapters"):
        raise SystemExit("Formal chapter router still uses /api/chapters")

print("runtime routes OK")
'@

$output = $routeCheck | & $python - 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $output
    Fail "Runtime route table check failed"
}
Write-Host "[mvp-routes] $output"

Write-Step "check v1.2 routes"

Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/story-bible?project_id=" "Story Bible API in DailyWriter"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/character-cards?project_id=" "Character Cards API in DailyWriter"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/world-entries?project_id=" "World Entries API in DailyWriter"
Require-Text "frontend/src/pages/DailyWriterPage.tsx" "/api/chapter-plans?project_id=" "Chapter Plans API in DailyWriter"
Require-Text "backend/services/daily_writer_service.py" "list_bibles" "Story Bible in prompt builder"
Require-Text "backend/services/daily_writer_service.py" "list_cards" "Character Cards in prompt builder"
Require-Text "backend/services/daily_writer_service.py" "list_entries" "World Entries in prompt builder"
Require-Text "backend/services/daily_writer_service.py" "get_plan_by_number" "Chapter Plan in prompt builder"

Write-Step "all MVP route checks passed"
