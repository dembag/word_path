""" Schema classes used by api routes."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

# Fields returned when creating AND returning user information
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age_band: Literal["0-5", "6-9", "10-13", "14-17", "18+"]
    prompt_display: Literal["text_only", "symbols_and_text"] = "symbols_and_text"
    locations: list[str] = Field(default_factory=list)
    card_size: Literal["small", "medium", "large"] = "medium"
    starting_format: Literal["choice", "sentence"] = "choice"


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    age_band: Literal["0-5", "6-9", "10-13", "14-17", "18+"] | None = None
    prompt_display: Literal["text_only", "symbols_and_text"] | None = None
    locations: list[str] | None = None
    card_size: Literal["small", "medium", "large"] | None = None
    starting_format: Literal["choice", "sentence"] | None = None


# Returned from API query
class UserResponse(UserBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    created_at: datetime


