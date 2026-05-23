"""Story Bible API 路由。"""

from fastapi import APIRouter, HTTPException, Path

from schemas.story_bible import StoryBible
from services.story_bible_service import load_story_bible

router = APIRouter(tags=["story-bible"])


@router.get("/projects/{project_id}/story-bible", response_model=StoryBible)
async def get_story_bible(
    project_id: str = Path(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="项目 ID，只能包含字母、数字、短横线和下划线。",
    )
) -> StoryBible:
    """获取指定项目的 Story Bible。

    示例：GET /projects/demo-project/story-bible
    """
    try:
        bible = load_story_bible(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return bible
