from datetime import datetime
from pydantic import BaseModel, Field


class CharacterCardCreate(BaseModel):
    project_id: int
    name: str = Field(default="", max_length=200)
    role: str = Field(default="", max_length=200)
    personality: str = Field(default="")
    motivation: str = Field(default="")
    conflict: str = Field(default="")
    relationship_notes: str = Field(default="")
    arc: str = Field(default="")


class CharacterCardUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    role: str | None = Field(default=None, max_length=200)
    personality: str | None = Field(default=None)
    motivation: str | None = Field(default=None)
    conflict: str | None = Field(default=None)
    relationship_notes: str | None = Field(default=None)
    arc: str | None = Field(default=None)


class CharacterCardListItem(BaseModel):
    id: int; project_id: int; name: str; role: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class CharacterCardRead(CharacterCardListItem):
    personality: str; motivation: str; conflict: str; relationship_notes: str; arc: str
    model_config = {"from_attributes": True}
