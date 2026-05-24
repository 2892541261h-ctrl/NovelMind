from datetime import datetime

from pydantic import BaseModel, Field


class ChapterCreate(BaseModel):
    project_id: int
    chapter_number: int = Field(default=0, ge=0)
    title: str = Field(default="", max_length=200)
    goal: str = Field(default="", max_length=2000)
    summary: str = Field(default="", max_length=5000)
    content: str = Field(default="", max_length=50000)
    involved_characters: str = Field(default="", max_length=2000)
    location: str = Field(default="", max_length=500)
    conflict: str = Field(default="", max_length=2000)
    ending_hook: str = Field(default="", max_length=2000)
    status: str = Field(default="draft", max_length=50)


class ChapterUpdate(BaseModel):
    chapter_number: int | None = Field(default=None, ge=0)
    title: str | None = Field(default=None, max_length=200)
    goal: str | None = Field(default=None, max_length=2000)
    summary: str | None = Field(default=None, max_length=5000)
    content: str | None = Field(default=None, max_length=50000)
    involved_characters: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None, max_length=500)
    conflict: str | None = Field(default=None, max_length=2000)
    ending_hook: str | None = Field(default=None, max_length=2000)
    status: str | None = Field(default=None, max_length=50)


class ChapterResponse(BaseModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    goal: str
    summary: str
    content: str
    involved_characters: str
    location: str
    conflict: str
    ending_hook: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
