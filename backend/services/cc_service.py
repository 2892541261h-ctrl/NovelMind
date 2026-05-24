from sqlalchemy.orm import Session
from models.character_card import CharacterCard
from schemas.character_card_schema import CharacterCardCreate, CharacterCardUpdate


def list_cards(db: Session, project_id: int) -> list[CharacterCard]:
    return db.query(CharacterCard).filter(CharacterCard.project_id == project_id).all()


def get_card(db: Session, card_id: int) -> CharacterCard | None:
    return db.query(CharacterCard).filter(CharacterCard.id == card_id).first()


def create_card(db: Session, data: CharacterCardCreate) -> CharacterCard:
    c = CharacterCard(**data.model_dump()); db.add(c); db.commit(); db.refresh(c); return c


def update_card(db: Session, card_id: int, data: CharacterCardUpdate) -> CharacterCard | None:
    c = db.query(CharacterCard).filter(CharacterCard.id == card_id).first()
    if not c: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(c, k, v)
    db.commit(); db.refresh(c); return c


def delete_card(db: Session, card_id: int) -> bool:
    c = db.query(CharacterCard).filter(CharacterCard.id == card_id).first()
    if not c: return False
    db.delete(c); db.commit(); return True
