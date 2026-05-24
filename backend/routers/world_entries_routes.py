from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.world_entry_schema import WorldEntryCreate, WorldEntryListItem, WorldEntryRead, WorldEntryUpdate
from services import we_service

router = APIRouter(prefix="/api/world-entries", tags=["world-entries"])

@router.get("", response_model=list[WorldEntryListItem])
def list_entries(project_id: int, db: Session = Depends(get_db)):
    return we_service.list_entries(db, project_id)

@router.post("", response_model=WorldEntryRead, status_code=201)
def create_entry(data: WorldEntryCreate, db: Session = Depends(get_db)):
    return we_service.create_entry(db, data)

@router.get("/{entry_id}", response_model=WorldEntryRead)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    e = we_service.get_entry(db, entry_id)
    if not e: raise HTTPException(404, "World entry not found")
    return e

@router.patch("/{entry_id}", response_model=WorldEntryRead)
def update_entry(entry_id: int, data: WorldEntryUpdate, db: Session = Depends(get_db)):
    e = we_service.update_entry(db, entry_id, data)
    if not e: raise HTTPException(404, "World entry not found")
    return e

@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    ok = we_service.delete_entry(db, entry_id)
    if not ok: raise HTTPException(404, "World entry not found")
