from sqlalchemy.orm import Session
from models.world_entry import WorldEntry
from schemas.world_entry_schema import WorldEntryCreate, WorldEntryUpdate


def list_entries(db: Session, project_id: int) -> list[WorldEntry]:
    return db.query(WorldEntry).filter(WorldEntry.project_id == project_id).all()


def get_entry(db: Session, entry_id: int) -> WorldEntry | None:
    return db.query(WorldEntry).filter(WorldEntry.id == entry_id).first()


def create_entry(db: Session, data: WorldEntryCreate) -> WorldEntry:
    e = WorldEntry(**data.model_dump()); db.add(e); db.commit(); db.refresh(e); return e


def update_entry(db: Session, entry_id: int, data: WorldEntryUpdate) -> WorldEntry | None:
    e = db.query(WorldEntry).filter(WorldEntry.id == entry_id).first()
    if not e: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(e, k, v)
    db.commit(); db.refresh(e); return e


def delete_entry(db: Session, entry_id: int) -> bool:
    e = db.query(WorldEntry).filter(WorldEntry.id == entry_id).first()
    if not e: return False
    db.delete(e); db.commit(); return True
