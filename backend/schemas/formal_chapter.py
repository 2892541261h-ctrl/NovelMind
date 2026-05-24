from datetime import datetime

from pydantic import BaseModel, Field


class FormalChapterCreate(BaseModel):
    project_id: int
    chapter_number: int = Field(default=0, ge=0)
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")
    status: str = Field(default="published", max_length=50)


class FormalChapterUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None)
    status: str | None = Field(default=None, max_length=50)


class FormalChapterListItem(BaseModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    status: str
    word_count: int
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FormalChapterRead(BaseModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    content: str
    status: str
    word_count: int
    source_draft_id: int | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublishDraftRequest(BaseModel):
    overwrite_existing: bool = False


class PublishDraftResponse(BaseModel):
    chapter: FormalChapterRead
    draft_kept: bool = True
