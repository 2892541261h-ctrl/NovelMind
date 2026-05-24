from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import settings
from database import Base, engine
from routers.ai import router as ai_router
from routers.ai_models_routes import router as ai_models_router
from routers.ai_providers_routes import router as ai_providers_router
from routers.ai_usage_logs_routes import router as ai_usage_logs_router
from routers.chapter import router as chapter_router
from routers.character_cards_routes import router as cc_routes_router
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
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NovelMind backend skeleton.",
    lifespan=lifespan,
)

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
