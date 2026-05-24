"""AI 请求/响应最小类型契约。"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field


ProviderName = Literal["mock"]


class AIMessage(BaseModel):
    """单条对话消息。"""
    role: Literal["system", "user", "assistant"] = "user"
    content: str = Field(min_length=1)


class AIRequest(BaseModel):
    """AI 生成请求。"""
    model: str = "mock-model"
    provider: ProviderName = "mock"
    messages: list[AIMessage] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=800, ge=1, le=4000)


class AIUsage(BaseModel):
    """token 用量信息。"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIResponse(BaseModel):
    """AI 生成响应。"""
    request_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    provider: ProviderName = "mock"
    model: str = "mock-model"
    text: str
    usage: AIUsage = Field(default_factory=AIUsage)
