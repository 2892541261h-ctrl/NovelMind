from fastapi import APIRouter

from ai import AIMessage, AIRequest, generate_text
from config import settings
from database import get_database_url


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_provider": settings.ai_provider,
        "database": get_database_url(),
    }


@router.get("/health/ai-mock")
async def ai_mock_check() -> dict:
    """最小 AI mock 示例接口：验证 gateway 能正常工作。"""
    request = AIRequest(
        model="mock-model",
        provider="mock",
        messages=[
            AIMessage(role="system", content="你是一个测试助手。"),
            AIMessage(role="user", content="你好，请确认 mock provider 正常工作。"),
        ],
        temperature=0.7,
        max_tokens=256,
    )
    response = await generate_text(request)
    return {
        "status": "ok",
        "provider": response.provider,
        "model": response.model,
        "request_id": response.request_id,
        "text": response.text,
        "usage": response.usage.model_dump(),
    }
