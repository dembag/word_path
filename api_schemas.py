""" Schema classes used by api routes."""
from datetime import datetime


from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated, Any, Literal

SESSION_QUESTION_COUNT = 5

AgeBand = Literal["0-5", "6-9", "10-13", "14-17", "18+"]
CardSize = Literal["small", "medium", "large"]
CommunicationGoal = Literal[
    "requesting",
    "sharing_information",
    "social_interaction",
    "communication_repair",
]
PracticeFormat = Literal["choice", "sentence"]
PromptDisplay = Literal["text_only", "symbols_and_text"]
SessionStatus = Literal["active", "completed"]

NonBlankStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


# ------ User schema ------
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
    name: str | None = Field(default=None, min_length=1, max_length=50)
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


# ------ Symbol schema ------
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


class UserSymbolBase(BaseModel):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    symbol_id: int
    page: str = Field(min_length=1, max_length=20)
    position: int


class UserSymbolResponse(BaseModel):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    symbol_id: int
    page: str = Field(min_length=1, max_length=20)
    position: int
    word: str = Field(min_length=1, max_length=20)
    word_class: str = Field(min_length=1, max_length=20)


# ------ Question schema ------
class LearnerQuestion(BaseModel):
    question_id: int
    location: NonBlankStr | None = Field(max_length=20, default=None)
    question_format: PracticeFormat
    communication_goal: CommunicationGoal
    question: NonBlankStr
    question_symbol_ids: list[int] = Field(min_length=1)
    available_symbol_ids: list[int] = Field(min_length=1)


class GeneratedQuestion(LearnerQuestion):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    expected_response: list[int] = Field(min_length=1)


class GeneratedQuestionBatch(BaseModel):
    questions: list[GeneratedQuestion] = Field(
        min_length=SESSION_QUESTION_COUNT,
        max_length=SESSION_QUESTION_COUNT,
    )


# ------ Practice session schema ------
class PracticeSessionBase(BaseModel):
    communication_goal: CommunicationGoal
    practice_format: PracticeFormat
    location: str | None = Field(max_length=20, default=None)
    session_status: SessionStatus = Field(default="active")
    summary: dict[str, Any] | None = None


class PracticeSessionResponse(PracticeSessionBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    user_id: int
    questions: list[LearnerQuestion] = Field(
        min_length=SESSION_QUESTION_COUNT,
        max_length=SESSION_QUESTION_COUNT,
    )
    started_at: datetime
    completed_at: datetime | None


class StartPracticeSession(BaseModel):
    user_id: int
    communication_goal: CommunicationGoal
    practice_format: PracticeFormat
    location: str | None = Field(max_length=20, default=None)
