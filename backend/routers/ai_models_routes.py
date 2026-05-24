from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.ai_model_config_schema import AIModelCreate, AIModelListItem, AIModelRead, AIModelUpdate
from services import amc_service

router = APIRouter(prefix="/api/ai/models", tags=["ai-models"])

@router.get("", response_model=list[AIModelListItem])
def list_models(provider_id: int | None = None, db: Session = Depends(get_db)):
    return amc_service.list_models(db, provider_id)

@router.post("", response_model=AIModelRead, status_code=201)
def create_model(data: AIModelCreate, db: Session = Depends(get_db)):
    return amc_service.create_model(db, data)

@router.get("/{model_id}", response_model=AIModelRead)
def get_model(model_id: int, db: Session = Depends(get_db)):
    m = amc_service.get_model(db, model_id)
    if not m: raise HTTPException(404, "Model not found")
    return m

@router.patch("/{model_id}", response_model=AIModelRead)
def update_model(model_id: int, data: AIModelUpdate, db: Session = Depends(get_db)):
    m = amc_service.update_model(db, model_id, data)
    if not m: raise HTTPException(404, "Model not found")
    return m

@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    ok = amc_service.delete_model(db, model_id)
    if not ok: raise HTTPException(404, "Model not found")

@router.post("/{model_id}/set-default", response_model=AIModelRead)
def set_default_model(model_id: int, db: Session = Depends(get_db)):
    m = amc_service.set_default(db, model_id)
    if not m: raise HTTPException(404, "Model not found")
    return m
