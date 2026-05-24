from sqlalchemy.orm import Session
from models.novel_story_bible import NovelStoryBible
from schemas.story_bible_schema import StoryBibleCreate, StoryBibleUpdate


def list_bibles(db: Session, project_id: int) -> list[NovelStoryBible]:
    return db.query(NovelStoryBible).filter(NovelStoryBible.project_id == project_id).all()


def get_bible(db: Session, bible_id: int) -> NovelStoryBible | None:
    return db.query(NovelStoryBible).filter(NovelStoryBible.id == bible_id).first()


def create_bible(db: Session, data: StoryBibleCreate) -> NovelStoryBible:
    sb = NovelStoryBible(**data.model_dump())
    db.add(sb); db.commit(); db.refresh(sb); return sb


def update_bible(db: Session, bible_id: int, data: StoryBibleUpdate) -> NovelStoryBible | None:
    sb = db.query(NovelStoryBible).filter(NovelStoryBible.id == bible_id).first()
    if not sb: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(sb, k, v)
    db.commit(); db.refresh(sb); return sb


def delete_bible(db: Session, bible_id: int) -> bool:
    sb = db.query(NovelStoryBible).filter(NovelStoryBible.id == bible_id).first()
    if not sb: return False
    db.delete(sb); db.commit(); return True
