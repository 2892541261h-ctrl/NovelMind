from datetime import datetime
from pydantic import BaseModel, Field


class StoryBibleCreate(BaseModel):
    project_id: int
    title: str = Field(default="", max_length=200)
    premise: str = Field(default="")
    genre: str = Field(default="", max_length=200)
    tone: str = Field(default="", max_length=500)
    theme: str = Field(default="")
    world_rules: str = Field(default="")
    narrative_style: str = Field(default="")


class StoryBibleUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    premise: str | None = Field(default=None)
    genre: str | None = Field(default=None, max_length=200)
    tone: str | None = Field(default=None, max_length=500)
    theme: str | None = Field(default=None)
    world_rules: str | None = Field(default=None)
    narrative_style: str | None = Field(default=None)


class StoryBibleListItem(BaseModel):
    id: int; project_id: int; title: str; genre: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class StoryBibleRead(StoryBibleListItem):
    premise: str; tone: str; theme: str; world_rules: str; narrative_style: str
    model_config = {"from_attributes": True}
