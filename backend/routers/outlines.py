from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.outline import Outline
from schemas.outline import OutlineCreate, OutlineUpdate, OutlineResponse

router = APIRouter(tags=["outlines"])


@router.get("/api/projects/{project_id}/outlines", response_model=list[OutlineResponse])
def list_outlines(project_id: int, db: Session = Depends(get_db)):
    return db.query(Outline).filter(Outline.project_id == project_id).all()


@router.post("/api/projects/{project_id}/outlines", response_model=OutlineResponse, status_code=201)
def create_outline(project_id: int, data: OutlineCreate, db: Session = Depends(get_db)):
    outline = Outline(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(outline)
    db.commit()
    db.refresh(outline)
    return outline


@router.get("/api/outlines/{outline_id}", response_model=OutlineResponse)
def get_outline(outline_id: int, db: Session = Depends(get_db)):
    outline = db.query(Outline).filter(Outline.id == outline_id).first()
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")
    return outline


@router.put("/api/outlines/{outline_id}", response_model=OutlineResponse)
def update_outline(outline_id: int, data: OutlineUpdate, db: Session = Depends(get_db)):
    outline = db.query(Outline).filter(Outline.id == outline_id).first()
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(outline, key, val)
    db.commit()
    db.refresh(outline)
    return outline


@router.delete("/api/outlines/{outline_id}", status_code=204)
def delete_outline(outline_id: int, db: Session = Depends(get_db)):
    outline = db.query(Outline).filter(Outline.id == outline_id).first()
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")
    db.delete(outline)
    db.commit()
