"""AI Gateway 基础测试 —— 不依赖真实 AI Provider，不调用网络。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from ai.gateway import generate_text  # noqa: E402
from ai.provider_factory import get_provider  # noqa: E402
from ai.providers.mock_provider import MockAIProvider  # noqa: E402
from ai.types import AIMessage, AIRequest  # noqa: E402


def _make_request(**kwargs) -> AIRequest:
    defaults = {
        "task": "test_task",
        "messages": [
            AIMessage(role="system", content="测试系统指令。"),
            AIMessage(role="user", content="测试用户输入。"),
        ],
    }
    defaults.update(kwargs)
    return AIRequest(**defaults)


class TestProviderFactory:
    """provider_factory 行为测试。"""

    def test_empty_provider_returns_mock(self) -> None:
        """provider 为空时返回 MockAIProvider。"""
        provider = get_provider(None)
        assert isinstance(provider, MockAIProvider)
        assert provider.provider_name == "mock"

    def test_mock_provider_returns_mock(self) -> None:
        """provider="mock" 时返回 MockAIProvider。"""
        provider = get_provider("mock")
        assert isinstance(provider, MockAIProvider)
        assert provider.provider_name == "mock"

    def test_unsupported_provider_raises(self) -> None:
        """不支持的 provider 抛出 ValueError。"""
        with pytest.raises(ValueError, match="不支持的 AI provider"):
            get_provider("unsupported-provider")


class TestMockProvider:
    """MockAIProvider 行为测试。"""

    def test_response_provider_is_mock(self) -> None:
        """mock response 中 provider 为 mock。"""
        response = asyncio.run(_gen_mock())
        assert response.provider == "mock"

    def test_response_error_is_none(self) -> None:
        """mock response 中 error 为 None。"""
        response = asyncio.run(_gen_mock())
        assert response.error is None

    def test_response_content_contains_task(self) -> None:
        """mock response 的 content 包含 task 名称。"""
        response = asyncio.run(_gen_mock(task="health_check"))
        assert "health_check" in response.content

    def test_response_has_usage(self) -> None:
        """mock response 包含 usage 信息。"""
        response = asyncio.run(_gen_mock())
        assert "total_tokens" in response.usage
        assert response.usage["total_tokens"] > 0

    def test_default_model_is_mock_novel_writer(self) -> None:
        """不指定 model 时默认为 mock-novel-writer。"""
        response = asyncio.run(_gen_mock(model=None))
        assert response.model == "mock-novel-writer"

    def test_custom_model_is_preserved(self) -> None:
        """指定 model 时保留用户指定的值。"""
        response = asyncio.run(_gen_mock(model="custom-model"))
        assert response.model == "custom-model"


class TestGateway:
    """gateway 统一入口测试。"""

    def test_default_uses_mock(self) -> None:
        """不指定 provider 时使用 mock。"""
        response = asyncio.run(_gen_via_gateway())
        assert response.provider == "mock"
        assert response.error is None

    def test_mock_provider_works(self) -> None:
        """provider="mock" 正常工作。"""
        response = asyncio.run(_gen_via_gateway(provider="mock"))
        assert response.provider == "mock"
        assert response.error is None
        assert len(response.content) > 0

    def test_unsupported_provider_returns_error(self) -> None:
        """不支持的 provider 返回 AIResponse 且 error 字段包含错误信息。"""
        response = asyncio.run(_gen_via_gateway(provider="unsupported-provider"))
        assert response.error is not None
        assert "不支持的 AI provider" in response.error
        assert response.content == ""

    def test_content_includes_task_name(self) -> None:
        """gateway 返回的 content 包含 task 名称。"""
        response = asyncio.run(_gen_via_gateway(task="test_gateway_task"))
        assert "test_gateway_task" in response.content
        assert response.error is None


async def _gen_mock(**kwargs) -> object:
    provider = MockAIProvider()
    request = _make_request(**kwargs)
    return await provider.generate(request)


async def _gen_via_gateway(**kwargs) -> object:
    request = _make_request(**kwargs)
    return await generate_text(request)
