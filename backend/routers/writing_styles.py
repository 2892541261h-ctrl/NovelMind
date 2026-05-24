from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.writing_style import WritingStyle
from schemas.writing_style import WritingStyleCreate, WritingStyleUpdate, WritingStyleResponse

router = APIRouter(tags=["writing-styles"])


@router.get("/api/projects/{project_id}/writing-styles", response_model=list[WritingStyleResponse])
def list_writing_styles(project_id: int, db: Session = Depends(get_db)):
    return db.query(WritingStyle).filter(WritingStyle.project_id == project_id).all()


@router.post("/api/projects/{project_id}/writing-styles", response_model=WritingStyleResponse, status_code=201)
def create_writing_style(project_id: int, data: WritingStyleCreate, db: Session = Depends(get_db)):
    ws = WritingStyle(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.get("/api/writing-styles/{style_id}", response_model=WritingStyleResponse)
def get_writing_style(style_id: int, db: Session = Depends(get_db)):
    ws = db.query(WritingStyle).filter(WritingStyle.id == style_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Writing style not found")
    return ws


@router.put("/api/writing-styles/{style_id}", response_model=WritingStyleResponse)
def update_writing_style(style_id: int, data: WritingStyleUpdate, db: Session = Depends(get_db)):
    ws = db.query(WritingStyle).filter(WritingStyle.id == style_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Writing style not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(ws, key, val)
    db.commit()
    db.refresh(ws)
    return ws


@router.delete("/api/writing-styles/{style_id}", status_code=204)
def delete_writing_style(style_id: int, db: Session = Depends(get_db)):
    ws = db.query(WritingStyle).filter(WritingStyle.id == style_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Writing style not found")
    db.delete(ws)
    db.commit()
