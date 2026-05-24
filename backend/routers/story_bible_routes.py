from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.story_bible_schema import StoryBibleCreate, StoryBibleListItem, StoryBibleRead, StoryBibleUpdate
from services import sb_service

router = APIRouter(prefix="/api/story-bible", tags=["story-bible"])

@router.get("", response_model=list[StoryBibleListItem])
def list_bibles(project_id: int, db: Session = Depends(get_db)):
    return sb_service.list_bibles(db, project_id)

@router.post("", response_model=StoryBibleRead, status_code=201)
def create_bible(data: StoryBibleCreate, db: Session = Depends(get_db)):
    return sb_service.create_bible(db, data)

@router.get("/{bible_id}", response_model=StoryBibleRead)
def get_bible(bible_id: int, db: Session = Depends(get_db)):
    sb = sb_service.get_bible(db, bible_id)
    if not sb: raise HTTPException(404, "Story Bible not found")
    return sb

@router.patch("/{bible_id}", response_model=StoryBibleRead)
def update_bible(bible_id: int, data: StoryBibleUpdate, db: Session = Depends(get_db)):
    sb = sb_service.update_bible(db, bible_id, data)
    if not sb: raise HTTPException(404, "Story Bible not found")
    return sb

@router.delete("/{bible_id}", status_code=204)
def delete_bible(bible_id: int, db: Session = Depends(get_db)):
    ok = sb_service.delete_bible(db, bible_id)
    if not ok: raise HTTPException(404, "Story Bible not found")
