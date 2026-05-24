from datetime import datetime
from pydantic import BaseModel, Field


class ChapterSummaryCreate(BaseModel):
    project_id: int; chapter_number: int = Field(default=0, ge=1)
    chapter_id: int | None = None
    summary: str = Field(default="")
    key_events: str = Field(default="")
    character_changes: str = Field(default="")
    unresolved_threads: str = Field(default="")


class ChapterSummaryUpdate(BaseModel):
    chapter_id: int | None = None
    summary: str | None = None
    key_events: str | None = None
    character_changes: str | None = None
    unresolved_threads: str | None = None


class ChapterSummaryListItem(BaseModel):
    id: int; project_id: int; chapter_number: int; chapter_id: int | None
    key_events: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ChapterSummaryRead(ChapterSummaryListItem):
    summary: str; character_changes: str; unresolved_threads: str
    model_config = {"from_attributes": True}
