""" Schema classes used by api routes."""
import datetime

from pydantic import BaseModel, ConfigDict, Field

# Fields returned when creating AND returning user information
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    vocab_tier: str = Field(min_length=1, max_length=50)
    learning_phase: int = Field(ge=0, le=10)
    learning_step: str = Field(min_length=1, max_length=20)
    ai_can_add_vocab: bool = False
    layout_locked: bool = True
    card_size: Literal["s", "m", "l"] = "m"

class UserCreate(UserBase):
    pass

# Returned from API query
class UserResponse(UserBase):
    # Allows access by dot notation to work eg. user.name
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    created_at: datetime


