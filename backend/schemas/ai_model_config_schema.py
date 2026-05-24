from datetime import datetime
from pydantic import BaseModel, Field


class AIModelCreate(BaseModel):
    provider_id: int
    name: str = Field(default="", max_length=200)
    model: str = Field(default="", max_length=200)
    display_name: str = Field(default="", max_length=200)
    context_window: int = Field(default=0, ge=0)
    input_price_per_1m_tokens: float | None = None
    output_price_per_1m_tokens: float | None = None
    currency: str = Field(default="USD", max_length=10)
    is_default: bool = False
    is_active: bool = True


class AIModelUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    model: str | None = Field(default=None, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    context_window: int | None = Field(default=None, ge=0)
    input_price_per_1m_tokens: float | None = None
    output_price_per_1m_tokens: float | None = None
    currency: str | None = Field(default=None, max_length=10)
    is_default: bool | None = None
    is_active: bool | None = None


class AIModelListItem(BaseModel):
    id: int; provider_id: int; name: str; model: str; display_name: str; is_default: bool; is_active: bool; created_at: datetime
    model_config = {"from_attributes": True}


class AIModelRead(AIModelListItem):
    context_window: int; input_price_per_1m_tokens: float | None; output_price_per_1m_tokens: float | None; currency: str; updated_at: datetime
    model_config = {"from_attributes": True}
