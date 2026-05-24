from datetime import datetime

from pydantic import BaseModel, Field


class ReferenceNovelCreate(BaseModel):
    project_id: int
    title: str = Field(default="", max_length=200)
    author: str = Field(default="", max_length=200)
    content: str = Field(default="")
    source_type: str = Field(default="paste", max_length=50)


class ReferenceNovelUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    author: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None)
    status: str | None = Field(default=None, max_length=50)


class ReferenceNovelResponse(BaseModel):
    id: int
    project_id: int
    title: str
    author: str
    content: str
    source_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
