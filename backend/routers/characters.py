from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.character import Character
from schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse

router = APIRouter(tags=["characters"])


@router.get("/api/projects/{project_id}/characters", response_model=list[CharacterResponse])
def list_characters(project_id: int, db: Session = Depends(get_db)):
    return db.query(Character).filter(Character.project_id == project_id).all()


@router.post("/api/projects/{project_id}/characters", response_model=CharacterResponse, status_code=201)
def create_character(project_id: int, data: CharacterCreate, db: Session = Depends(get_db)):
    char = Character(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(char)
    db.commit()
    db.refresh(char)
    return char


@router.get("/api/characters/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char


@router.put("/api/characters/{character_id}", response_model=CharacterResponse)
def update_character(character_id: int, data: CharacterUpdate, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(char, key, val)
    db.commit()
    db.refresh(char)
    return char


@router.delete("/api/characters/{character_id}", status_code=204)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(char)
    db.commit()
