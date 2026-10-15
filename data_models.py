""" Model of the tables in the database"""
from __future__ import annotations      # so forward references work on older python versions

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from sqlalchemy.dialects.postgresql import JSONB

from data_manager import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # User age band 0-5, 6-9, 10-13, 14-17, 18+ (affects scenario themes)
    age_band: Mapped[str] = mapped_column(String, nullable=False)

    # Prompt display mode ('text_only' or 'symbols_and_text')
    prompt_display: Mapped[str] = mapped_column(
        String(20), default="symbols_and_text", nullable=False
    )

    # Starting practice format ('choice' or 'sentence')
    starting_format: Mapped[str] = mapped_column(
        String(8), default="choice", nullable=False
    )

    # Optional locations
    locations : Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )

    # Card sizes ('small', 'medium', 'large')
    card_size: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    default=lambda: datetime.now(UTC),
    )

    # Table relationship/s
    goal_links: Mapped[list[UserGoal]] = relationship(back_populates="user")


class CommunicationGoal(Base):
    __tablename__ = "communication_goals"

    goal_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Goals ('requesting', 'sharing_information', 'social_interaction'
    # and 'communication_repair')
    goal_name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Table relationship/s
    user_links: Mapped[list[UserGoal]] = relationship(back_populates="goal")


class UserGoal(Base):
    __tablename__ = "user_goals"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False
    )

    goal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("communication_goals.goal_id"), primary_key=True,
        nullable=False
    )

    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Table relationship/s
    user: Mapped["User"] = relationship(back_populates="goal_links")
    goal: Mapped["CommunicationGoal"] = relationship(back_populates="user_links")
