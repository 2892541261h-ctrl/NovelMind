from datetime import datetime
from pydantic import BaseModel, Field


class PlotThreadCreate(BaseModel):
    project_id: int
    title: str = Field(default="", max_length=200)
    description: str = Field(default="")
    status: str = Field(default="open", max_length=50)
    introduced_chapter: int = Field(default=0, ge=0)
    resolved_chapter: int = Field(default=0, ge=0)
    notes: str = Field(default="")


class PlotThreadUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    status: str | None = Field(default=None, max_length=50)
    introduced_chapter: int | None = Field(default=None, ge=0)
    resolved_chapter: int | None = Field(default=None, ge=0)
    notes: str | None = None


class PlotThreadListItem(BaseModel):
    id: int; project_id: int; title: str; status: str; introduced_chapter: int; resolved_chapter: int; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class PlotThreadRead(PlotThreadListItem):
    description: str; notes: str
    model_config = {"from_attributes": True}
