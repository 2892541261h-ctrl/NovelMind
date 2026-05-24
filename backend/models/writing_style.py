from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class WritingStyle(Base):
    __tablename__ = "writing_styles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(String(2000), default="")
    sentence_style: Mapped[str] = mapped_column(String(2000), default="")
    vocabulary_style: Mapped[str] = mapped_column(String(2000), default="")
    dialogue_style: Mapped[str] = mapped_column(String(2000), default="")
    description_style: Mapped[str] = mapped_column(String(2000), default="")
    emotion_style: Mapped[str] = mapped_column(String(2000), default="")
    pacing_style: Mapped[str] = mapped_column(String(2000), default="")
    forbidden_style: Mapped[str] = mapped_column(String(2000), default="")
    strength: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
