"""Novel Project API 路由。"""

from fastapi import APIRouter, HTTPException, Path

from schemas.novel_project import NovelProjectDetail, NovelProjectSummary
from services.novel_project_service import get_novel_project, list_novel_projects

router = APIRouter(tags=["novel-project"])


@router.get("/projects", response_model=list[NovelProjectSummary])
async def list_projects() -> list[NovelProjectSummary]:
    """列出所有小说项目。

    返回 novels/ 下所有有效项目的摘要。
    """
    return list_novel_projects()


@router.get(
    "/projects/{project_id}",
    response_model=NovelProjectDetail,
)
async def get_project(
    project_id: str = Path(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="项目 ID，只能包含字母、数字、短横线和下划线。",
    )
) -> NovelProjectDetail:
    """获取指定小说项目的详细信息。

    示例：GET /projects/demo-project
    """
    try:
        return get_novel_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
