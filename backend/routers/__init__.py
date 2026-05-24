"""后端路由模块。"""

from .ai import router as ai_router
from .chapter import router as chapter_router
from .health import router as health_router
from .novel_project import router as novel_project_router
from .project_config import router as project_config_router
from .story_bible import router as story_bible_router
from .writer import router as writer_router

__all__ = [
    "ai_router",
    "chapter_router",
    "health_router",
    "novel_project_router",
    "project_config_router",
    "story_bible_router",
    "writer_router",
]
