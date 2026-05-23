"""后端路由模块。"""

from .health import router as health_router
from .novel_project import router as novel_project_router
from .story_bible import router as story_bible_router

__all__ = [
    "health_router",
    "novel_project_router",
    "story_bible_router",
]
