from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text

from config import settings
from database import Base, engine
from routers.ai import router as ai_router
from routers.ai_models_routes import router as ai_models_router
from routers.ai_providers_routes import router as ai_providers_router
from routers.ai_usage_logs_routes import router as ai_usage_logs_router
from routers.chapter import router as chapter_router
from routers.character_cards_routes import router as cc_routes_router
from routers.dashboard_routes import router as dashboard_router
from routers.characters import router as characters_router
from routers.chapter_plans_routes import router as cp_routes_router
from routers.chapter_reviews_routes import router as cr_review_router
from routers.chapter_summaries_routes import router as cs_routes_router
from routers.continuity_routes import router as continuity_router
from routers.daily_writer import router as daily_writer_router
from routers.chapters import router as chapters_router
from routers.exports import router as exports_router
from routers.formal_chapters import router as formal_chapters_router
from routers.foreshadowing import router as foreshadowing_router
from routers.health import router as health_router
from routers.novel_project import router as novel_project_router
from routers.outlines import router as outlines_router
from routers.plot_threads_routes import router as pt_routes_router
from routers.project_config import router as project_config_router
from routers.projects import router as projects_router
from routers.reference_novels import router as reference_novels_router
from routers.story_bible import router as story_bible_router
from routers.story_bible_routes import router as sb_routes_router
from routers.world_entries_routes import router as we_routes_router
from routers.world_settings import router as world_settings_router
from routers.writer import router as writer_router
from routers.writing_styles import router as writing_styles_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_schema()
    yield


def _ensure_sqlite_schema() -> None:
    """Apply tiny SQLite compatibility fixes for local V1 databases."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as conn:
        inspector = inspect(conn)
        table_names = set(inspector.get_table_names())
        if "ai_provider_configs" not in table_names:
            return
        provider_columns = {col["name"] for col in inspector.get_columns("ai_provider_configs")}
        if "api_key_mode" not in provider_columns:
            conn.execute(
                text(
                    "ALTER TABLE ai_provider_configs "
                    "ADD COLUMN api_key_mode VARCHAR(20) NOT NULL DEFAULT 'env_var'"
                )
            )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NovelMind backend skeleton.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Vite dev server
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        # Electron desktop — frontend served from backend via /app
        # When Electron loads from http://127.0.0.1:8765/app, the origin
        # is http://127.0.0.1:8765.  The frontend uses relative paths
        # (same-origin) so CORS is only needed for browser dev scenarios.
        "http://127.0.0.1:8765",
        "http://localhost:8765",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Frontend static files (Electron desktop same-origin hosting) ──────────────
# In development, frontend is served by Vite (port 5173).
# In Electron/production, the frontend dist/ is served by this backend
# under /app/* so the origin matches (http://127.0.0.1:8765).
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


# SPA fallback: serve /app and /app/* → index.html
@app.get("/app")
@app.get("/app/{full_path:path}")
async def serve_spa(full_path: str = ""):
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"detail": "Frontend not built. Run: cd frontend && npm run build"}, 503


# Mount frontend assets at /assets/ for absolute-path SPA routing
assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


app.include_router(health_router)
app.include_router(ai_router)
app.include_router(novel_project_router)
app.include_router(project_config_router)
app.include_router(chapter_router)
app.include_router(story_bible_router)
app.include_router(writer_router)
app.include_router(projects_router)
app.include_router(characters_router)
app.include_router(world_settings_router)
app.include_router(outlines_router)
app.include_router(chapters_router)
app.include_router(foreshadowing_router)
app.include_router(writing_styles_router)
app.include_router(reference_novels_router)
app.include_router(daily_writer_router)
app.include_router(formal_chapters_router)
app.include_router(exports_router)
app.include_router(ai_providers_router)
app.include_router(ai_models_router)
app.include_router(ai_usage_logs_router)
app.include_router(dashboard_router)
app.include_router(sb_routes_router)
app.include_router(cc_routes_router)
app.include_router(we_routes_router)
app.include_router(cp_routes_router)
app.include_router(cs_routes_router)
app.include_router(pt_routes_router)
app.include_router(cr_review_router)
app.include_router(continuity_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ready",
    }
