from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from ai.gateway import test_provider_connection
from schemas.ai_provider_config_schema import AIProviderCreate, AIProviderListItem, AIProviderRead, AIProviderUpdate
from services import apc_service
from services.local_secret_service import save_api_key, delete_api_key, get_status


class LocalKeyRequest(BaseModel):
    api_key: str = Field(min_length=1)


class LocalKeyStatus(BaseModel):
    has_direct_api_key: bool
    masked_api_key: str


class TestConnectionResponse(BaseModel):
    ok: bool
    message: str


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
    delete_api_key(provider_id)
    ok = apc_service.delete_provider(db, provider_id)
    if not ok: raise HTTPException(404, "Provider not found")


@router.post("/{provider_id}/local-key")
def save_local_key(provider_id: int, req: LocalKeyRequest, db: Session = Depends(get_db)):
    p = apc_service.get_provider(db, provider_id)
    if not p: raise HTTPException(404, "Provider not found")
    save_api_key(provider_id, req.api_key)
    return LocalKeyStatus(has_direct_api_key=True, masked_api_key=get_status(provider_id)["masked_api_key"])


@router.delete("/{provider_id}/local-key")
def delete_local_key(provider_id: int, db: Session = Depends(get_db)):
    p = apc_service.get_provider(db, provider_id)
    if not p: raise HTTPException(404, "Provider not found")
    delete_api_key(provider_id)
    return LocalKeyStatus(has_direct_api_key=False, masked_api_key="")


@router.get("/{provider_id}/local-key/status", response_model=LocalKeyStatus)
def get_local_key_status(provider_id: int, db: Session = Depends(get_db)):
    p = apc_service.get_provider(db, provider_id)
    if not p: raise HTTPException(404, "Provider not found")
    return LocalKeyStatus(**get_status(provider_id))


@router.post("/{provider_id}/test", response_model=TestConnectionResponse)
async def test_connection(provider_id: int, db: Session = Depends(get_db)):
    p = apc_service.get_provider(db, provider_id)
    if not p: raise HTTPException(404, "Provider not found")
    ok, message = await test_provider_connection(p)
    return TestConnectionResponse(ok=ok, message=message)
