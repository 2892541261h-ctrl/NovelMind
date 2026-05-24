from datetime import datetime

from pydantic import BaseModel, Field


class ChapterDraftGenerateRequest(BaseModel):
    project_id: int
    chapter_number: int = Field(..., ge=1)
    title: str = Field(default="", max_length=200)
    writing_goal: str = Field(default="")
    extra_instruction: str = Field(default="")
    allow_new_version: bool = False


class ChapterDraftCreate(BaseModel):
    project_id: int
    chapter_number: int = Field(default=0, ge=0)
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")
    status: str = Field(default="draft", max_length=50)
    source: str = Field(default="daily_writer", max_length=50)
    writing_goal: str = Field(default="")
    prompt_snapshot: str = Field(default="")
    context_snapshot: str = Field(default="")


class ChapterDraftListItem(BaseModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterDraftRead(BaseModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    content: str
    status: str
    source: str
    writing_goal: str
    prompt_snapshot: str
    context_snapshot: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterDraftGenerateResponse(BaseModel):
    draft: ChapterDraftRead
    existing_replaced: bool = False
