"""AI Provider 抽象基类。"""

from abc import ABC, abstractmethod

from ..types import AIRequest, AIResponse, ProviderName


class BaseAIProvider(ABC):
    """所有 AI Provider 的抽象基类。"""

    @property
    @abstractmethod
    def provider_name(self) -> ProviderName:
        raise NotImplementedError

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError
