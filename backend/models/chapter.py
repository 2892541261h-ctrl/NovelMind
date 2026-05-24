from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(200), default="")
    goal: Mapped[str] = mapped_column(String(2000), default="")
    summary: Mapped[str] = mapped_column(String(5000), default="")
    content: Mapped[str] = mapped_column(String(50000), default="")
    involved_characters: Mapped[str] = mapped_column(String(2000), default="")
    location: Mapped[str] = mapped_column(String(500), default="")
    conflict: Mapped[str] = mapped_column(String(2000), default="")
    ending_hook: Mapped[str] = mapped_column(String(2000), default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
