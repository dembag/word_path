""" Schema classes used by api routes."""
from datetime import datetime


from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal


AgeBand = Literal["0-5", "6-9", "10-13", "14-17", "18+"]

PracticeFormat = Literal["choice", "sentence"]

PromptDisplay = Literal["text_only", "symbols_and_text"]

CardSize = Literal["small", "medium", "large"]

CommunicationGoal = Literal[
    "requesting",
    "sharing_information",
    "social_interaction",
    "communication_repair",
]

SessionStatus = Literal["active", "completed"]



# Fields returned when creating AND returning user information
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age_band: AgeBand
    prompt_display: PromptDisplay = "symbols_and_text"
    starting_format: PracticeFormat = "choice"
    locations: list[str] = Field(default_factory=list)
    communication_goals: list[CommunicationGoal] = Field(default_factory=list)
    card_size: CardSize = "medium"



class UserCreate(UserBase):
    pass


# Used for updating the user's profile
class UserUpdate(BaseModel):
    age_band: AgeBand | None = None
    prompt_display: PromptDisplay | None = None
    starting_format: PracticeFormat | None = None
    locations: list[str] | None = None
    communication_goals: list[CommunicationGoal] | None = None
    card_size: CardSize | None = None


# Returned from API query
class UserResponse(UserBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    created_at: datetime


# Symbol schema
class SymbolBase(BaseModel):
    word: str = Field(min_length=1, max_length=20)
    word_class: str = Field(min_length=3, max_length=20)
    source: str | None = Field(max_length=100, default=None)
    source_id: str | None = Field(max_length=100, default=None)

    # Path to image file
    image_reference: str = Field(min_length=5, max_length=200)

    author: str | None = Field(max_length=50, default=None)
    license: str | None = Field(max_length=50, default=None)

    # Formatted symbol credits
    attribution: str | None = Field(max_length=200, default=None)


class SymbolResponse(SymbolBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    symbol_id: int
    user_id: int


# Practice session schema
class PracticeSessionBase(BaseModel):
    communication_goal: CommunicationGoal
    practice_format: PracticeFormat
    scenario: dict[str, Any]
    session_status: SessionStatus = Field(default="active")
    summary: dict[str, Any] | None = None


class PracticeSessionResponse(PracticeSessionBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    user_id: int
    started_at: datetime
    completed_at: datetime | None
