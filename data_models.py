""" Model of the tables in the database"""
from __future__ import annotations      # so forward references work on older python versions

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_manager import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Current phase 0 - 6, changes on caregiver approval
    learning_phase: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Learning steps: guided | partial | independent
    learning_step: Mapped[str] = mapped_column(String(20), default='guided', nullable=False)

    ai_can_add_vocab: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    card_size: Mapped[str] = mapped_column(String(10), default='m', nullable=False)    # sizes: s, m, l

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    default=lambda: datetime.now(UTC),
    )


