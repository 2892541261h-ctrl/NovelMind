from datetime import datetime

from pydantic import BaseModel, Field


class ForeshadowingCreate(BaseModel):
    project_id: int
    title: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=3000)
    planted_chapter: int = Field(default=0, ge=0)
    expected_reveal_chapter: int = Field(default=0, ge=0)
    actual_reveal_chapter: int = Field(default=0, ge=0)
    status: str = Field(default="planted", max_length=50)
    importance: str = Field(default="medium", max_length=50)


class ForeshadowingUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=3000)
    planted_chapter: int | None = Field(default=None, ge=0)
    expected_reveal_chapter: int | None = Field(default=None, ge=0)
    actual_reveal_chapter: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=50)
    importance: str | None = Field(default=None, max_length=50)


class ForeshadowingResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    planted_chapter: int
    expected_reveal_chapter: int
    actual_reveal_chapter: int
    status: str
    importance: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
