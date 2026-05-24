from sqlalchemy.orm import Session
from models.plot_thread import PlotThread as PlotThreadModel
from schemas.plot_thread_schema import PlotThreadCreate, PlotThreadUpdate


def list_threads(db: Session, project_id: int) -> list[PlotThreadModel]:
    return db.query(PlotThreadModel).filter(PlotThreadModel.project_id == project_id).all()


def get_thread(db: Session, thread_id: int) -> PlotThreadModel | None:
    return db.query(PlotThreadModel).filter(PlotThreadModel.id == thread_id).first()


def create_thread(db: Session, data: PlotThreadCreate) -> PlotThreadModel:
    t = PlotThreadModel(**data.model_dump()); db.add(t); db.commit(); db.refresh(t); return t


def update_thread(db: Session, thread_id: int, data: PlotThreadUpdate) -> PlotThreadModel | None:
    t = db.query(PlotThreadModel).filter(PlotThreadModel.id == thread_id).first()
    if not t: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(t, k, v)
    db.commit(); db.refresh(t); return t


def delete_thread(db: Session, thread_id: int) -> bool:
    t = db.query(PlotThreadModel).filter(PlotThreadModel.id == thread_id).first()
    if not t: return False
    db.delete(t); db.commit(); return True


def get_open_threads(db: Session, project_id: int) -> list[PlotThreadModel]:
    return db.query(PlotThreadModel).filter(PlotThreadModel.project_id == project_id, PlotThreadModel.status.in_(["open", "developing"])).all()
