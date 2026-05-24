from sqlalchemy.orm import Session
from models.ai_provider_config import AIProviderConfig
from schemas.ai_provider_config_schema import AIProviderCreate, AIProviderUpdate


def list_providers(db: Session) -> list[AIProviderConfig]:
    return db.query(AIProviderConfig).all()


def get_provider(db: Session, provider_id: int) -> AIProviderConfig | None:
    return db.query(AIProviderConfig).filter(AIProviderConfig.id == provider_id).first()


def get_active_provider(db: Session) -> AIProviderConfig | None:
    return db.query(AIProviderConfig).filter(AIProviderConfig.is_active == True).first()


def get_default_provider(db: Session) -> AIProviderConfig | None:
    return get_active_provider(db)


def create_provider(db: Session, data: AIProviderCreate) -> AIProviderConfig:
    p = AIProviderConfig(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return p


def update_provider(db: Session, provider_id: int, data: AIProviderUpdate) -> AIProviderConfig | None:
    p = db.query(AIProviderConfig).filter(AIProviderConfig.id == provider_id).first()
    if not p: return None
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(p, k, v)
    db.commit(); db.refresh(p); return p


def delete_provider(db: Session, provider_id: int) -> bool:
    p = db.query(AIProviderConfig).filter(AIProviderConfig.id == provider_id).first()
    if not p: return False
    from models.ai_model_config import AIModelConfig
    db.query(AIModelConfig).filter(AIModelConfig.provider_id == provider_id).delete()
    db.delete(p); db.commit(); return True
