from datetime import datetime
from pydantic import BaseModel, Field


class ChapterReviewListItem(BaseModel):
    id: int; project_id: int; chapter_number: int; overall_score: float; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ChapterReviewRead(ChapterReviewListItem):
    draft_id: int | None; formal_chapter_id: int | None
    continuity_score: float; character_consistency_score: float; pacing_score: float
    style_score: float; originality_score: float; goal_alignment_score: float
    issues: str; suggestions: str
    model_config = {"from_attributes": True}


class SuggestRewriteResponse(BaseModel):
    suggested_title: str = ""
    suggested_outline: str = ""
    suggested_revision_notes: str = ""
    suggested_text: str = ""
