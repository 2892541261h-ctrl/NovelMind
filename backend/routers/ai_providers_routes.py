from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
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
    import os
    from services.local_secret_service import get_api_key
    key = None
    if p.api_key_mode == "direct_local":
        key = get_api_key(provider_id)
    elif p.api_key_env_var:
        key = os.environ.get(p.api_key_env_var, "")
    if not key:
        return TestConnectionResponse(ok=False, message="未配置 API Key，请在 AI 设置中填写密钥或配置环境变量。")
    try:
        import json, urllib.request
        url = (p.base_url or "").rstrip("/") + "/chat/completions"
        body = json.dumps({"model": p.default_model or "gpt-4o-mini", "messages": [{"role":"user","content":"OK"}], "max_tokens": 5}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"}, method="POST")
        urllib.request.urlopen(req, timeout=15)
        return TestConnectionResponse(ok=True, message="连接成功，可以开始写作。")
    except Exception as e:
        msg = str(e)[:200]
        if "401" in msg or "403" in msg: msg = "API Key 无效或无权限"
        elif "404" in msg: msg = "Base URL 或模型路径错误"
        elif "timeout" in msg.lower(): msg = "连接超时，请检查 Base URL 是否可访问"
        elif "refused" in msg.lower(): msg = "连接被拒绝，请检查 Base URL 端口"
        return TestConnectionResponse(ok=False, message=f"连接失败：{msg}")
