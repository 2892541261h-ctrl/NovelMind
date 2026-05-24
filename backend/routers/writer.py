"""Writer 写作上下文预览 API 路由。"""

from fastapi import APIRouter, HTTPException, Path

from schemas.writer_context import NextChapterPreview, PromptPreview, WriterContext
from services.writer_context_service import (
    build_writer_context,
    preview_next_chapter,
    preview_prompt,
)

router = APIRouter(tags=["writer"])

PID_PATH = Path(
    ...,
    pattern=r"^[A-Za-z0-9_-]+$",
    description="项目 ID，只能包含字母、数字、短横线和下划线。",
)


@router.get(
    "/projects/{project_id}/writer/context",
    response_model=WriterContext,
)
async def get_writer_context(
    project_id: str = PID_PATH,
) -> WriterContext:
    """构建完整写作上下文。

    组合项目详情、Story Bible、章节列表、大纲、风格配置、自动化配置和摘要。
    缺失的配置文件记录到 warnings 中，不阻塞整体返回。
    """
    try:
        return build_writer_context(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/writer/next-chapter-preview",
    response_model=NextChapterPreview,
)
async def get_next_chapter_preview(
    project_id: str = PID_PATH,
) -> NextChapterPreview:
    """预览下一章信息（只预览，不创建文件）。

    根据已有章节推断下一个 chapter_id 和 order。
    如果目标章节文件已存在，would_overwrite 为 true。
    """
    try:
        return preview_next_chapter(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/projects/{project_id}/writer/prompt-preview",
    response_model=PromptPreview,
)
async def get_prompt_preview(
    project_id: str = PID_PATH,
) -> PromptPreview:
    """返回 mock prompt 预览。

    这里只用于本地检查 prompt 形态，不执行 AI 生成。
    任何真正的 AI 生成都必须通过 `backend/ai/gateway.py`。
    """
    try:
        return preview_prompt(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
