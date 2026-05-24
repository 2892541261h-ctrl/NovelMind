from sqlalchemy.orm import Session
from models.chapter_summary import ChapterSummary as ChapterSummaryModel
from schemas.chapter_summary_schema import ChapterSummaryCreate, ChapterSummaryUpdate


def list_summaries(db: Session, project_id: int) -> list[ChapterSummaryModel]:
    return db.query(ChapterSummaryModel).filter(ChapterSummaryModel.project_id == project_id).order_by(ChapterSummaryModel.chapter_number).all()


def get_summary(db: Session, summary_id: int) -> ChapterSummaryModel | None:
    return db.query(ChapterSummaryModel).filter(ChapterSummaryModel.id == summary_id).first()


def create_summary(db: Session, data: ChapterSummaryCreate) -> ChapterSummaryModel:
    s = ChapterSummaryModel(**data.model_dump()); db.add(s); db.commit(); db.refresh(s); return s


def update_summary(db: Session, summary_id: int, data: ChapterSummaryUpdate) -> ChapterSummaryModel | None:
    s = db.query(ChapterSummaryModel).filter(ChapterSummaryModel.id == summary_id).first()
    if not s: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(s, k, v)
    db.commit(); db.refresh(s); return s


def delete_summary(db: Session, summary_id: int) -> bool:
    s = db.query(ChapterSummaryModel).filter(ChapterSummaryModel.id == summary_id).first()
    if not s: return False
    db.delete(s); db.commit(); return True


def get_recent_summaries(db: Session, project_id: int, limit: int = 5) -> list[ChapterSummaryModel]:
    return db.query(ChapterSummaryModel).filter(ChapterSummaryModel.project_id == project_id).order_by(ChapterSummaryModel.chapter_number.desc()).limit(limit).all()
