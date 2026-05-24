from datetime import datetime
from pydantic import BaseModel


class UsageLogListItem(BaseModel):
    id: int; feature_name: str; provider_type: str; model: str; status: str
    total_tokens: int | None; estimated_cost: float | None; latency_ms: int | None; created_at: datetime
    model_config = {"from_attributes": True}


class UsageLogRead(UsageLogListItem):
    provider_id: int | None; model_config_id: int | None
    input_tokens: int | None; output_tokens: int | None
    currency: str; estimated: bool; error_message: str; prompt_preview: str; response_preview: str
    model_config = {"from_attributes": True}


class UsageSummary(BaseModel):
    total_calls: int = 0
    total_success: int = 0
    total_error: int = 0
    total_tokens: int = 0
    total_estimated_cost: float = 0.0
    currency: str = "USD"
    by_feature: list[dict] = []
    by_model: list[dict] = []
