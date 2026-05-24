from datetime import datetime

from pydantic import BaseModel, Field


class ReferenceProfileCreate(BaseModel):
    novel_id: int
    project_id: int


class ReferenceProfileResponse(BaseModel):
    id: int
    novel_id: int
    project_id: int
    genre: str
    worldbuilding_pattern: str
    character_archetypes: str
    conflict_patterns: str
    writing_style_profile: str
    plot_progression_model: str
    target_novel_direction: str
    confidence: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
