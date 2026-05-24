"""统一 AI 调用入口。

外部模块应仅通过此模块调用 AI 能力，不应直接引用 providers 子包。
"""

from .provider_factory import create_provider
from .types import AIRequest, AIResponse


async def generate_text(request: AIRequest) -> AIResponse:
    """统一 AI 生成入口。

    当前骨架阶段仅支持 mock provider。
    """
    provider = create_provider(request.provider)
    return await provider.generate(request)
