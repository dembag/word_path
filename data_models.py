""" Model of the tables in the database"""
from __future__ import annotations      # so forward references work on older python versions
from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

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
    locations: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    # Communication goals
    # ('requesting', 'sharing_information', 'social_interaction', 'communication_repair')
    communication_goals: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )

    # Card sizes ('small', 'medium', 'large')
    card_size: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    default=lambda: datetime.now(UTC),
    )


class UserSymbol(Base):
    __tablename__ = "user_symbols"

    symbol_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False,)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False,)

    word: Mapped[str] = mapped_column(String(20), nullable=False,)
    word_class: Mapped[str] = mapped_column(String(20), nullable=False,)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True,)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True,)

    # Path to image file
    image_reference: Mapped[str] = mapped_column(String(200), nullable=False,)

    author: Mapped[str | None] = mapped_column(String(50), nullable=True,)
    license: Mapped[str | None] = mapped_column(String(50), nullable=True,)

    # Formatted symbol credits, eg. 'Author: <name>; source: <name>; licence: <licence_code>'
    attribution: Mapped[str | None] = mapped_column(String(200), nullable=True,)


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False,)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False,)

    communication_goal: Mapped[str] = mapped_column(String(20), nullable=False,)
    practice_format: Mapped[str] = mapped_column(String(8), nullable=False,)
    scenario: Mapped[dict] = mapped_column(JSON, nullable=False,)

    # Session status ('active', 'completed')
    status: Mapped[str] = mapped_column(String(9), default="active", nullable=False,)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True,)

