"""Mock AI Provider —— 不调用网络、不读取环境变量。"""

import uuid

from .base import BaseAIProvider
from ..types import AIRequest, AIResponse


class MockAIProvider(BaseAIProvider):
    """返回稳定 mock 文本，usage 使用假数据。"""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate(self, request: AIRequest) -> AIResponse:
        user_input = _extract_user_content(request.messages)
        mock_content = (
            f"[MockAIProvider] task={request.task}, "
            f"messages={len(request.messages)}, "
            f"last_user_input=\"{user_input}\"。"
            f" 这是 mock provider 返回的固定示例文本，用于验证 AI Gateway 基础结构是否正常工作。"
        )
        return AIResponse(
            provider="mock",
            model=request.model or "mock-novel-writer",
            content=mock_content,
            raw={"mock_generated": True, "task": request.task},
            usage={
                "prompt_tokens": len(user_input) // 4 + 1,
                "completion_tokens": len(mock_content) // 4 + 1,
                "total_tokens": (len(user_input) + len(mock_content)) // 4 + 2,
            },
            error=None,
        )


def _extract_user_content(messages: list) -> str:
    for msg in reversed(messages):
        role = getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        if role == "user" and content:
            return content
    return "（无用户消息）"
