"""AI Gateway 测试路由。"""

from fastapi import APIRouter

from ai import AIMessage, AIRequest, generate_text
from ai.types import AIResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/test", response_model=AIResponse)
async def ai_test() -> AIResponse:
    """AI Gateway 测试接口。

    通过 backend/ai/gateway.py 调用 mock provider，验证 AI 调用链路正常。
    """
    request = AIRequest(
        task="health_check",
        messages=[
            AIMessage(role="system", content="你是一个测试助手。"),
            AIMessage(role="user", content="请确认 AI Gateway 正常工作。"),
        ],
    )
    return await generate_text(request)
