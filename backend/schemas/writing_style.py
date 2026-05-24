from datetime import datetime

from pydantic import BaseModel, Field


class WritingStyleCreate(BaseModel):
    project_id: int
    name: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=2000)
    sentence_style: str = Field(default="", max_length=2000)
    vocabulary_style: str = Field(default="", max_length=2000)
    dialogue_style: str = Field(default="", max_length=2000)
    description_style: str = Field(default="", max_length=2000)
    emotion_style: str = Field(default="", max_length=2000)
    pacing_style: str = Field(default="", max_length=2000)
    forbidden_style: str = Field(default="", max_length=2000)
    strength: str = Field(default="", max_length=2000)


class WritingStyleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    sentence_style: str | None = Field(default=None, max_length=2000)
    vocabulary_style: str | None = Field(default=None, max_length=2000)
    dialogue_style: str | None = Field(default=None, max_length=2000)
    description_style: str | None = Field(default=None, max_length=2000)
    emotion_style: str | None = Field(default=None, max_length=2000)
    pacing_style: str | None = Field(default=None, max_length=2000)
    forbidden_style: str | None = Field(default=None, max_length=2000)
    strength: str | None = Field(default=None, max_length=2000)


class WritingStyleResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str
    sentence_style: str
    vocabulary_style: str
    dialogue_style: str
    description_style: str
    emotion_style: str
    pacing_style: str
    forbidden_style: str
    strength: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
