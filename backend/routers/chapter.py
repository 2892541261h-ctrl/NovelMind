"""Chapter API 路由。"""

from fastapi import APIRouter, HTTPException, Path

from schemas.chapter import ChapterContent, ChapterSummary
from services.chapter_service import get_chapter, list_chapters

router = APIRouter(tags=["chapter"])


@router.get(
    "/projects/{project_id}/chapters",
    response_model=list[ChapterSummary],
)
async def list_project_chapters(
    project_id: str = Path(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="项目 ID，只能包含字母、数字、短横线和下划线。",
    )
) -> list[ChapterSummary]:
    """列出指定项目的所有章节。

    如果项目没有 chapters 目录或目录为空，返回空列表。
    示例：GET /projects/demo-project/chapters
    """
    try:
        return list_chapters(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/chapters/{chapter_id}",
    response_model=ChapterContent,
)
async def get_project_chapter(
    project_id: str = Path(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="项目 ID，只能包含字母、数字、短横线和下划线。",
    ),
    chapter_id: str = Path(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="章节 ID，对应文件名（不含扩展名），只能包含字母、数字、短横线和下划线。",
    ),
) -> ChapterContent:
    """获取指定章节的完整内容。

    示例：GET /projects/demo-project/chapters/ch01
    """
    try:
        return get_chapter(project_id, chapter_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
