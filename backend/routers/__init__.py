from .ai import router as ai_router
from .chapter import router as chapter_router
from .characters import router as characters_router
from .chapters import router as chapters_router
from .foreshadowing import router as foreshadowing_router
from .health import router as health_router
from .novel_project import router as novel_project_router
from .outlines import router as outlines_router
from .project_config import router as project_config_router
from .projects import router as projects_router
from .story_bible import router as story_bible_router
from .world_settings import router as world_settings_router
from .writer import router as writer_router
from .writing_styles import router as writing_styles_router

__all__ = [
    "ai_router",
    "chapter_router",
    "characters_router",
    "chapters_router",
    "foreshadowing_router",
    "health_router",
    "novel_project_router",
    "outlines_router",
    "project_config_router",
    "projects_router",
    "story_bible_router",
    "world_settings_router",
    "writer_router",
    "writing_styles_router",
]
