from datetime import datetime

from pydantic import BaseModel, Field


class OutlineCreate(BaseModel):
    project_id: int
    title: str = Field(default="", max_length=200)
    one_sentence_pitch: str = Field(default="", max_length=500)
    theme: str = Field(default="", max_length=500)
    tone: str = Field(default="", max_length=500)
    act_one: str = Field(default="", max_length=5000)
    act_two: str = Field(default="", max_length=5000)
    act_three: str = Field(default="", max_length=5000)
    key_turning_points: str = Field(default="", max_length=3000)
    ending_direction: str = Field(default="", max_length=2000)


class OutlineUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    one_sentence_pitch: str | None = Field(default=None, max_length=500)
    theme: str | None = Field(default=None, max_length=500)
    tone: str | None = Field(default=None, max_length=500)
    act_one: str | None = Field(default=None, max_length=5000)
    act_two: str | None = Field(default=None, max_length=5000)
    act_three: str | None = Field(default=None, max_length=5000)
    key_turning_points: str | None = Field(default=None, max_length=3000)
    ending_direction: str | None = Field(default=None, max_length=2000)


class OutlineResponse(BaseModel):
    id: int
    project_id: int
    title: str
    one_sentence_pitch: str
    theme: str
    tone: str
    act_one: str
    act_two: str
    act_three: str
    key_turning_points: str
    ending_direction: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
