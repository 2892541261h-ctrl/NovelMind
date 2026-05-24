from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.chapter_summary_schema import ChapterSummaryCreate, ChapterSummaryListItem, ChapterSummaryRead, ChapterSummaryUpdate
from services import cs_service

router = APIRouter(prefix="/api/chapter-summaries", tags=["chapter-summaries"])

@router.get("", response_model=list[ChapterSummaryListItem])
def list_summaries(project_id: int, db: Session = Depends(get_db)):
    return cs_service.list_summaries(db, project_id)

@router.post("", response_model=ChapterSummaryRead, status_code=201)
def create_summary(data: ChapterSummaryCreate, db: Session = Depends(get_db)):
    return cs_service.create_summary(db, data)

@router.get("/{summary_id}", response_model=ChapterSummaryRead)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    s = cs_service.get_summary(db, summary_id)
    if not s: raise HTTPException(404, "Chapter summary not found")
    return s

@router.patch("/{summary_id}", response_model=ChapterSummaryRead)
def update_summary(summary_id: int, data: ChapterSummaryUpdate, db: Session = Depends(get_db)):
    s = cs_service.update_summary(db, summary_id, data)
    if not s: raise HTTPException(404, "Chapter summary not found")
    return s

@router.delete("/{summary_id}", status_code=204)
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    ok = cs_service.delete_summary(db, summary_id)
    if not ok: raise HTTPException(404, "Chapter summary not found")
