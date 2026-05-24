from datetime import datetime
from pydantic import BaseModel, Field


class AIProviderCreate(BaseModel):
    name: str = Field(default="", max_length=200)
    provider_type: str = Field(default="mock", max_length=50)
    base_url: str = Field(default="", max_length=500)
    api_key_env_var: str = Field(default="", max_length=200)
    api_key_mode: str = Field(default="env_var", max_length=20)
    default_model: str = Field(default="", max_length=200)
    is_active: bool = False


class AIProviderUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    provider_type: str | None = Field(default=None, max_length=50)
    base_url: str | None = Field(default=None, max_length=500)
    api_key_env_var: str | None = Field(default=None, max_length=200)
    api_key_mode: str | None = Field(default=None, max_length=20)
    default_model: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


class AIProviderListItem(BaseModel):
    id: int; name: str; provider_type: str; api_key_mode: str; default_model: str; is_active: bool; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class AIProviderRead(AIProviderListItem):
    base_url: str; api_key_env_var: str
    model_config = {"from_attributes": True}
