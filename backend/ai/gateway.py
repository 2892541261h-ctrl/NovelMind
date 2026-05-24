"""统一 AI 调用入口。

外部模块必须仅通过此模块调用 AI 能力，不得直接引用 providers 子包。
"""

from .provider_factory import get_provider
from .types import AIRequest, AIResponse


async def generate_text(request: AIRequest) -> AIResponse:
    """统一 AI 生成入口。

    发生异常时返回 AIResponse，error 字段包含错误信息，不抛出未处理异常。
    """
    try:
        provider = get_provider(request.provider)
        return await provider.generate(request)
    except Exception as exc:
        return AIResponse(
            provider=request.provider or "unknown",
            model=request.model or "unknown",
            content="",
            raw={},
            usage={},
            error=str(exc),
        )
