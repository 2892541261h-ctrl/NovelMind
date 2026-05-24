"""项目配置读取 API 路由。"""

from fastapi import APIRouter, HTTPException, Path

from schemas.project_config import (
    AutomationConfig,
    OutlineConfig,
    StyleProfileConfig,
    SummariesList,
)
from services.project_config_service import (
    list_summaries,
    load_automation,
    load_outline,
    load_style_profile,
)

router = APIRouter(tags=["project-config"])

PID_PATH = Path(
    ...,
    pattern=r"^[A-Za-z0-9_-]+$",
    description="项目 ID，只能包含字母、数字、短横线和下划线。",
)


@router.get(
    "/projects/{project_id}/outline",
    response_model=OutlineConfig,
)
async def get_outline(
    project_id: str = PID_PATH,
) -> OutlineConfig:
    """读取项目大纲配置。"""
    try:
        return load_outline(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/style-profile",
    response_model=StyleProfileConfig,
)
async def get_style_profile(
    project_id: str = PID_PATH,
) -> StyleProfileConfig:
    """读取项目写作风格配置。"""
    try:
        return load_style_profile(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/automation",
    response_model=AutomationConfig,
)
async def get_automation(
    project_id: str = PID_PATH,
) -> AutomationConfig:
    """读取项目自动化配置。"""
    try:
        return load_automation(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/summaries",
    response_model=SummariesList,
)
async def get_summaries(
    project_id: str = PID_PATH,
) -> SummariesList:
    """列出项目摘要文件。"""
    try:
        return list_summaries(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
