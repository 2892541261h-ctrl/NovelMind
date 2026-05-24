from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="")
    age: Mapped[int] = mapped_column(Integer, default=0)
    gender: Mapped[str] = mapped_column(String(50), default="")
    role_type: Mapped[str] = mapped_column(String(100), default="")
    appearance: Mapped[str] = mapped_column(String(2000), default="")
    personality: Mapped[str] = mapped_column(String(2000), default="")
    background: Mapped[str] = mapped_column(String(3000), default="")
    goal: Mapped[str] = mapped_column(String(2000), default="")
    secret: Mapped[str] = mapped_column(String(2000), default="")
    speaking_style: Mapped[str] = mapped_column(String(1000), default="")
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
