from sqlalchemy.orm import Session
from models.ai_model_config import AIModelConfig
from schemas.ai_model_config_schema import AIModelCreate, AIModelUpdate


def list_models(db: Session, provider_id: int | None = None) -> list[AIModelConfig]:
    q = db.query(AIModelConfig)
    if provider_id is not None: q = q.filter(AIModelConfig.provider_id == provider_id)
    return q.all()


def get_model(db: Session, model_id: int) -> AIModelConfig | None:
    return db.query(AIModelConfig).filter(AIModelConfig.id == model_id).first()


def get_default_model(db: Session) -> AIModelConfig | None:
    return db.query(AIModelConfig).filter(AIModelConfig.is_default == True, AIModelConfig.is_active == True).first()


def create_model(db: Session, data: AIModelCreate) -> AIModelConfig:
    m = AIModelConfig(**data.model_dump()); db.add(m); db.commit(); db.refresh(m); return m


def update_model(db: Session, model_id: int, data: AIModelUpdate) -> AIModelConfig | None:
    m = db.query(AIModelConfig).filter(AIModelConfig.id == model_id).first()
    if not m: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(m, k, v)
    db.commit(); db.refresh(m); return m


def delete_model(db: Session, model_id: int) -> bool:
    m = db.query(AIModelConfig).filter(AIModelConfig.id == model_id).first()
    if not m: return False
    db.delete(m); db.commit(); return True


def set_default(db: Session, model_id: int) -> AIModelConfig | None:
    m = db.query(AIModelConfig).filter(AIModelConfig.id == model_id).first()
    if not m: return None
    db.query(AIModelConfig).filter(AIModelConfig.provider_id == m.provider_id).update({"is_default": False})
    m.is_default = True; db.commit(); db.refresh(m); return m
