from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.chapter_draft import (
    ChapterDraftGenerateRequest,
    ChapterDraftGenerateResponse,
    ChapterDraftListItem,
    ChapterDraftRead,
)
from services import chapter_draft_service as drafts
from services.daily_writer_service import build_prompt

router = APIRouter(prefix="/api/daily-writer", tags=["daily-writer"])


@router.post("/generate", response_model=ChapterDraftGenerateResponse, status_code=201)
async def generate_chapter(
    req: ChapterDraftGenerateRequest, db: Session = Depends(get_db)
):
    try:
        draft = await drafts.generate_draft(db, req, build_prompt)
        return ChapterDraftGenerateResponse(
            draft=drafts.to_read(draft),
            existing_replaced=False,
        )
    except ValueError as exc:
        msg = str(exc)
        if "already exists" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=422, detail=msg)


@router.get("/chapters", response_model=list[ChapterDraftListItem])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    return [drafts.to_list_item(d) for d in drafts.list_drafts(db, project_id)]


@router.get("/chapters/{draft_id}", response_model=ChapterDraftRead)
def get_chapter(draft_id: int, db: Session = Depends(get_db)):
    draft = drafts.get_draft(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Chapter draft not found")
    return drafts.to_read(draft)


@router.delete("/chapters/{draft_id}", status_code=204)
def delete_chapter(draft_id: int, db: Session = Depends(get_db)):
    ok = drafts.delete_draft(db, draft_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Chapter draft not found")
