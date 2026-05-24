"""Provider 工厂 —— 根据名称获取 AI Provider 实例。"""

from .providers.base import BaseAIProvider
from .providers.mock_provider import MockAIProvider


def get_provider(provider_name: str | None) -> BaseAIProvider:
    """获取 AI Provider 实例。

    Args:
        provider_name: provider 名称。为 None 或空字符串时默认返回 mock。

    Returns:
        BaseAIProvider 实例。

    Raises:
        ValueError: 当 provider_name 不受支持且不为空时。
    """
    name = (provider_name or "").strip().lower()

    if not name or name == "mock":
        return MockAIProvider()

    raise ValueError(
        f'不支持的 AI provider："{provider_name}"。当前只支持：mock。'
    )
