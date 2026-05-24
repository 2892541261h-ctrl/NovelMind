from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class AIModelConfig(Base):
    __tablename__ = "ai_model_configs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_provider_configs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="")
    model: Mapped[str] = mapped_column(String(200), default="")
    display_name: Mapped[str] = mapped_column(String(200), default="")
    context_window: Mapped[int] = mapped_column(Integer, default=0)
    input_price_per_1m_tokens: Mapped[float | None] = mapped_column(Float, nullable=True)
    output_price_per_1m_tokens: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
