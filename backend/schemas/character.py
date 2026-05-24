from datetime import datetime

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    project_id: int
    name: str = Field(default="", max_length=200)
    age: int = Field(default=0, ge=0)
    gender: str = Field(default="", max_length=50)
    role_type: str = Field(default="", max_length=100)
    appearance: str = Field(default="", max_length=2000)
    personality: str = Field(default="", max_length=2000)
    background: str = Field(default="", max_length=3000)
    goal: str = Field(default="", max_length=2000)
    secret: str = Field(default="", max_length=2000)
    speaking_style: str = Field(default="", max_length=1000)
    status: str = Field(default="active", max_length=50)


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    age: int | None = Field(default=None, ge=0)
    gender: str | None = Field(default=None, max_length=50)
    role_type: str | None = Field(default=None, max_length=100)
    appearance: str | None = Field(default=None, max_length=2000)
    personality: str | None = Field(default=None, max_length=2000)
    background: str | None = Field(default=None, max_length=3000)
    goal: str | None = Field(default=None, max_length=2000)
    secret: str | None = Field(default=None, max_length=2000)
    speaking_style: str | None = Field(default=None, max_length=1000)
    status: str | None = Field(default=None, max_length=50)


class CharacterResponse(BaseModel):
    id: int
    project_id: int
    name: str
    age: int
    gender: str
    role_type: str
    appearance: str
    personality: str
    background: str
    goal: str
    secret: str
    speaking_style: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
