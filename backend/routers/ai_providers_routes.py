from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.ai_provider_config_schema import AIProviderCreate, AIProviderListItem, AIProviderRead, AIProviderUpdate
from services import apc_service

router = APIRouter(prefix="/api/ai/providers", tags=["ai-providers"])

@router.get("", response_model=list[AIProviderListItem])
def list_providers(db: Session = Depends(get_db)):
    return apc_service.list_providers(db)

@router.post("", response_model=AIProviderRead, status_code=201)
def create_provider(data: AIProviderCreate, db: Session = Depends(get_db)):
    return apc_service.create_provider(db, data)

@router.get("/{provider_id}", response_model=AIProviderRead)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    p = apc_service.get_provider(db, provider_id)
    if not p: raise HTTPException(404, "Provider not found")
    return p

@router.patch("/{provider_id}", response_model=AIProviderRead)
def update_provider(provider_id: int, data: AIProviderUpdate, db: Session = Depends(get_db)):
    p = apc_service.update_provider(db, provider_id, data)
    if not p: raise HTTPException(404, "Provider not found")
    return p

@router.delete("/{provider_id}", status_code=204)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    ok = apc_service.delete_provider(db, provider_id)
    if not ok: raise HTTPException(404, "Provider not found")
