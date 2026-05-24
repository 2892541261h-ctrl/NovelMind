from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import settings
from database import Base, engine
from routers.ai import router as ai_router
from routers.chapter import router as chapter_router
from routers.characters import router as characters_router
from routers.chapters import router as chapters_router
from routers.foreshadowing import router as foreshadowing_router
from routers.health import router as health_router
from routers.novel_project import router as novel_project_router
from routers.outlines import router as outlines_router
from routers.project_config import router as project_config_router
from routers.projects import router as projects_router
from routers.reference_novels import router as reference_novels_router
from routers.story_bible import router as story_bible_router
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


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ready",
    }
