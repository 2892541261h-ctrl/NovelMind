from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ChapterSummary(Base):
    __tablename__ = "chapter_summaries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    chapter_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chapter_number: Mapped[int] = mapped_column(Integer, default=1)
    summary: Mapped[str] = mapped_column(Text, default="")
    key_events: Mapped[str] = mapped_column(Text, default="")
    character_changes: Mapped[str] = mapped_column(Text, default="")
    unresolved_threads: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
