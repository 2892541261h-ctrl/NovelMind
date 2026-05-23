from fastapi import FastAPI

from config import settings
from routers.health import router as health_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NovelMind backend skeleton.",
)

app.include_router(health_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ready",
    }
