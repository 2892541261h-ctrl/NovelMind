from datetime import datetime
from pydantic import BaseModel, Field


class WorldEntryCreate(BaseModel):
    project_id: int
    name: str = Field(default="", max_length=200)
    entry_type: str = Field(default="other", max_length=50)
    description: str = Field(default="")
    rules: str = Field(default="")
    importance: str = Field(default="medium", max_length=50)


class WorldEntryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    entry_type: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None)
    rules: str | None = Field(default=None)
    importance: str | None = Field(default=None, max_length=50)


class WorldEntryListItem(BaseModel):
    id: int; project_id: int; name: str; entry_type: str; importance: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class WorldEntryRead(WorldEntryListItem):
    description: str; rules: str
    model_config = {"from_attributes": True}
