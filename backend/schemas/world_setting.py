from datetime import datetime

from pydantic import BaseModel, Field


class WorldSettingCreate(BaseModel):
    project_id: int
    name: str = Field(default="", max_length=200)
    category: str = Field(default="", max_length=100)
    content: str = Field(default="", max_length=5000)
    rules: str = Field(default="", max_length=3000)
    limitations: str = Field(default="", max_length=3000)
    importance: str = Field(default="medium", max_length=50)


class WorldSettingUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    content: str | None = Field(default=None, max_length=5000)
    rules: str | None = Field(default=None, max_length=3000)
    limitations: str | None = Field(default=None, max_length=3000)
    importance: str | None = Field(default=None, max_length=50)


class WorldSettingResponse(BaseModel):
    id: int
    project_id: int
    name: str
    category: str
    content: str
    rules: str
    limitations: str
    importance: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
