from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.character_card_schema import CharacterCardCreate, CharacterCardListItem, CharacterCardRead, CharacterCardUpdate
from services import cc_service

router = APIRouter(prefix="/api/character-cards", tags=["character-cards"])

@router.get("", response_model=list[CharacterCardListItem])
def list_cards(project_id: int, db: Session = Depends(get_db)):
    return cc_service.list_cards(db, project_id)

@router.post("", response_model=CharacterCardRead, status_code=201)
def create_card(data: CharacterCardCreate, db: Session = Depends(get_db)):
    return cc_service.create_card(db, data)

@router.get("/{card_id}", response_model=CharacterCardRead)
def get_card(card_id: int, db: Session = Depends(get_db)):
    c = cc_service.get_card(db, card_id)
    if not c: raise HTTPException(404, "Character card not found")
    return c

@router.patch("/{card_id}", response_model=CharacterCardRead)
def update_card(card_id: int, data: CharacterCardUpdate, db: Session = Depends(get_db)):
    c = cc_service.update_card(db, card_id, data)
    if not c: raise HTTPException(404, "Character card not found")
    return c

@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    ok = cc_service.delete_card(db, card_id)
    if not ok: raise HTTPException(404, "Character card not found")
