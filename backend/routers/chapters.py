from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.chapter import Chapter
from schemas.db_chapter import ChapterCreate, ChapterUpdate, ChapterResponse

router = APIRouter(tags=["chapters"])


@router.get("/api/projects/{project_id}/chapters", response_model=list[ChapterResponse])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    return db.query(Chapter).filter(Chapter.project_id == project_id).order_by(Chapter.chapter_number).all()


@router.post("/api/projects/{project_id}/chapters", response_model=ChapterResponse, status_code=201)
def create_chapter(project_id: int, data: ChapterCreate, db: Session = Depends(get_db)):
    chapter = Chapter(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/api/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/api/chapters/{chapter_id}", response_model=ChapterResponse)
def update_chapter(chapter_id: int, data: ChapterUpdate, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(chapter, key, val)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.delete("/api/chapters/{chapter_id}", status_code=204)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(chapter)
    db.commit()
