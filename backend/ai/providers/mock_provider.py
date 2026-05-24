"""Mock AI Provider —— 不调用网络、不读取环境变量。"""

import uuid

from .base import BaseAIProvider
from ..types import AIRequest, AIResponse, AIUsage, ProviderName


class MockAIProvider(BaseAIProvider):
    """返回固定但可读的 mock 文本，usage 使用假数据。"""

    @property
    def provider_name(self) -> ProviderName:
        return "mock"

    async def generate(self, request: AIRequest) -> AIResponse:
        # 根据输入 messages 构建一段可读的 mock 回复
        user_input = _extract_user_content(request.messages)
        mock_text = (
            f"[MockAIProvider] 已收到 {len(request.messages)} 条消息。"
            f" 用户最后输入：{user_input}。"
            f" 请求参数：model={request.model}, "
            f"temperature={request.temperature}, "
            f"max_tokens={request.max_tokens}。"
            f" 这是一段由 mock provider 生成的固定示例文本，"
            f"用于验证 AI Gateway 最小契约是否正常工作。"
        )
        return AIResponse(
            request_id=uuid.uuid4().hex,
            provider="mock",
            model=request.model,
            text=mock_text,
            usage=AIUsage(
                prompt_tokens=len(user_input) // 4 + 1,
                completion_tokens=len(mock_text) // 4 + 1,
                total_tokens=(len(user_input) + len(mock_text)) // 4 + 2,
            ),
        )


def _extract_user_content(messages: list) -> str:
    for msg in reversed(messages):
        role = getattr(msg, "role", None) or getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        if role == "user" and content:
            return content
    return "（无用户消息）"
