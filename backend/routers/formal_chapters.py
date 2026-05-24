from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.formal_chapter import (
    FormalChapterListItem,
    FormalChapterRead,
    FormalChapterUpdate,
    PublishDraftResponse,
)
from services import formal_chapter_service as fsvc

router = APIRouter(prefix="/api/formal-chapters", tags=["formal-chapters"])


@router.get("", response_model=list[FormalChapterListItem])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    chapters = fsvc.list_chapters(db, project_id)
    return [FormalChapterListItem.model_validate(c) for c in chapters]


@router.get("/{chapter_id}", response_model=FormalChapterRead)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    ch = fsvc.get_chapter(db, chapter_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return FormalChapterRead.model_validate(ch)


@router.patch("/{chapter_id}", response_model=FormalChapterRead)
def update_chapter(chapter_id: int, data: FormalChapterUpdate, db: Session = Depends(get_db)):
    ch = fsvc.update_chapter(db, chapter_id, data)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return FormalChapterRead.model_validate(ch)


@router.delete("/{chapter_id}", status_code=204)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    ok = fsvc.delete_chapter(db, chapter_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Chapter not found")


@router.post("/publish-draft/{draft_id}", response_model=PublishDraftResponse, status_code=201)
def publish_draft(draft_id: int, db: Session = Depends(get_db)):
    try:
        chapter = fsvc.publish_draft(db, draft_id, overwrite_existing=False)
        return PublishDraftResponse(
            chapter=FormalChapterRead.model_validate(chapter),
            draft_kept=True,
        )
    except ValueError as exc:
        msg = str(exc)
        if "already exists" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=422, detail=msg)
