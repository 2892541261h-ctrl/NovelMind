from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(default="", max_length=200)
    genre: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=2000)
    target_word_count: int = Field(default=0, ge=0)
    status: str = Field(default="planning", max_length=50)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    genre: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    target_word_count: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=50)


class ProjectResponse(BaseModel):
    id: int
    title: str
    genre: str
    description: str
    target_word_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
