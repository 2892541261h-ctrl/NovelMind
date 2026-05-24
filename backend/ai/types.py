"""AI 请求/响应统一类型契约。"""

import uuid
from typing import Any
from typing import Literal

from pydantic import BaseModel, Field

ProviderName = Literal["mock"]


class AIMessage(BaseModel):
    """单条对话消息。"""
    role: str = "user"
    content: str = Field(min_length=1)


class AIRequest(BaseModel):
    """AI 生成请求。"""
    task: str = Field(min_length=1)
    messages: list[AIMessage] = Field(default_factory=list)
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    response_format: str | None = None


class AIResponse(BaseModel):
    """AI 生成响应。"""
    request_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    provider: str = ""
    model: str = ""
    content: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
