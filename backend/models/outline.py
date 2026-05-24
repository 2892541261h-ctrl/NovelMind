from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Outline(Base):
    __tablename__ = "outlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="")
    one_sentence_pitch: Mapped[str] = mapped_column(String(500), default="")
    theme: Mapped[str] = mapped_column(String(500), default="")
    tone: Mapped[str] = mapped_column(String(500), default="")
    act_one: Mapped[str] = mapped_column(String(5000), default="")
    act_two: Mapped[str] = mapped_column(String(5000), default="")
    act_three: Mapped[str] = mapped_column(String(5000), default="")
    key_turning_points: Mapped[str] = mapped_column(String(3000), default="")
    ending_direction: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
