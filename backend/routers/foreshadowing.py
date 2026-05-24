from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.foreshadowing import Foreshadowing
from schemas.foreshadowing import ForeshadowingCreate, ForeshadowingUpdate, ForeshadowingResponse

router = APIRouter(tags=["foreshadowing"])


@router.get("/api/projects/{project_id}/foreshadowing", response_model=list[ForeshadowingResponse])
def list_foreshadowing(project_id: int, db: Session = Depends(get_db)):
    return db.query(Foreshadowing).filter(Foreshadowing.project_id == project_id).all()


@router.post("/api/projects/{project_id}/foreshadowing", response_model=ForeshadowingResponse, status_code=201)
def create_foreshadowing(project_id: int, data: ForeshadowingCreate, db: Session = Depends(get_db)):
    fs = Foreshadowing(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


@router.get("/api/foreshadowing/{foreshadowing_id}", response_model=ForeshadowingResponse)
def get_foreshadowing(foreshadowing_id: int, db: Session = Depends(get_db)):
    fs = db.query(Foreshadowing).filter(Foreshadowing.id == foreshadowing_id).first()
    if not fs:
        raise HTTPException(status_code=404, detail="Foreshadowing not found")
    return fs


@router.put("/api/foreshadowing/{foreshadowing_id}", response_model=ForeshadowingResponse)
def update_foreshadowing(foreshadowing_id: int, data: ForeshadowingUpdate, db: Session = Depends(get_db)):
    fs = db.query(Foreshadowing).filter(Foreshadowing.id == foreshadowing_id).first()
    if not fs:
        raise HTTPException(status_code=404, detail="Foreshadowing not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(fs, key, val)
    db.commit()
    db.refresh(fs)
    return fs


@router.delete("/api/foreshadowing/{foreshadowing_id}", status_code=204)
def delete_foreshadowing(foreshadowing_id: int, db: Session = Depends(get_db)):
    fs = db.query(Foreshadowing).filter(Foreshadowing.id == foreshadowing_id).first()
    if not fs:
        raise HTTPException(status_code=404, detail="Foreshadowing not found")
    db.delete(fs)
    db.commit()
