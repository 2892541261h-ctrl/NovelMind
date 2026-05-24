from datetime import datetime
from pydantic import BaseModel, Field


class ChapterPlanCreate(BaseModel):
    project_id: int; chapter_number: int = Field(..., ge=1)
    title: str = Field(default="", max_length=200)
    goal: str = Field(default="")
    key_events: str = Field(default="")
    pov_character: str = Field(default="", max_length=200)
    status: str = Field(default="planned", max_length=50)


class ChapterPlanUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    goal: str | None = Field(default=None)
    key_events: str | None = Field(default=None)
    pov_character: str | None = Field(default=None, max_length=200)
    status: str | None = Field(default=None, max_length=50)


class ChapterPlanListItem(BaseModel):
    id: int; project_id: int; chapter_number: int; title: str; goal: str; status: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ChapterPlanRead(ChapterPlanListItem):
    key_events: str; pov_character: str
    model_config = {"from_attributes": True}
