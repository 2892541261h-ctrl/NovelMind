from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ReferenceProfile(Base):
    __tablename__ = "reference_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("reference_novels.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    genre: Mapped[str] = mapped_column(String(200), default="")
    worldbuilding_pattern: Mapped[str] = mapped_column(Text, default="")
    character_archetypes: Mapped[str] = mapped_column(Text, default="")
    conflict_patterns: Mapped[str] = mapped_column(Text, default="")
    writing_style_profile: Mapped[str] = mapped_column(Text, default="")
    plot_progression_model: Mapped[str] = mapped_column(Text, default="")
    target_novel_direction: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[str] = mapped_column(String(50), default="low")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
