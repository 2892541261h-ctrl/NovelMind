from sqlalchemy.orm import Session
from models.chapter_plan import ChapterPlan
from schemas.chapter_plan_schema import ChapterPlanCreate, ChapterPlanUpdate


def list_plans(db: Session, project_id: int) -> list[ChapterPlan]:
    return db.query(ChapterPlan).filter(ChapterPlan.project_id == project_id).order_by(ChapterPlan.chapter_number).all()


def get_plan(db: Session, plan_id: int) -> ChapterPlan | None:
    return db.query(ChapterPlan).filter(ChapterPlan.id == plan_id).first()


def get_plan_by_number(db: Session, project_id: int, chapter_number: int) -> ChapterPlan | None:
    return db.query(ChapterPlan).filter(ChapterPlan.project_id == project_id, ChapterPlan.chapter_number == chapter_number).first()


def create_plan(db: Session, data: ChapterPlanCreate) -> ChapterPlan:
    existing = get_plan_by_number(db, data.project_id, data.chapter_number)
    if existing:
        raise ValueError(f"Chapter plan {data.chapter_number} already exists for project {data.project_id}")
    cp = ChapterPlan(**data.model_dump()); db.add(cp); db.commit(); db.refresh(cp); return cp


def update_plan(db: Session, plan_id: int, data: ChapterPlanUpdate) -> ChapterPlan | None:
    cp = db.query(ChapterPlan).filter(ChapterPlan.id == plan_id).first()
    if not cp: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(cp, k, v)
    db.commit(); db.refresh(cp); return cp


def delete_plan(db: Session, plan_id: int) -> bool:
    cp = db.query(ChapterPlan).filter(ChapterPlan.id == plan_id).first()
    if not cp: return False
    db.delete(cp); db.commit(); return True
