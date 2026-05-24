from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ChapterReview(Base):
    __tablename__ = "chapter_reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    draft_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    formal_chapter_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chapter_number: Mapped[int] = mapped_column(Integer, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    continuity_score: Mapped[float] = mapped_column(Float, default=0.0)
    character_consistency_score: Mapped[float] = mapped_column(Float, default=0.0)
    pacing_score: Mapped[float] = mapped_column(Float, default=0.0)
    style_score: Mapped[float] = mapped_column(Float, default=0.0)
    originality_score: Mapped[float] = mapped_column(Float, default=0.0)
    goal_alignment_score: Mapped[float] = mapped_column(Float, default=0.0)
    issues: Mapped[str] = mapped_column(Text, default="")
    suggestions: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
