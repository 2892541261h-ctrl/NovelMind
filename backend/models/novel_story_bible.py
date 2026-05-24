from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class NovelStoryBible(Base):
    __tablename__ = "novel_story_bibles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="")
    premise: Mapped[str] = mapped_column(Text, default="")
    genre: Mapped[str] = mapped_column(String(200), default="")
    tone: Mapped[str] = mapped_column(String(500), default="")
    theme: Mapped[str] = mapped_column(Text, default="")
    world_rules: Mapped[str] = mapped_column(Text, default="")
    narrative_style: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
