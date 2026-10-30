import random
from operator import itemgetter

from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated
from sqlalchemy import delete, select, desc
from sqlalchemy.orm import Session

from data_manager import Base, engine, get_db, SessionLocal
from dummy_data import SCENARIOS, SYMBOL_CATALOG
import data_models as dm

from api_schemas import (
    GeneratedQuestionBatch,
    PracticeSessionResponse,
    StartPracticeSession,
    SymbolResponse,
    UserCreate,
    UserResponse,
    UserSymbolBase,
    UserSymbolResponse,
    UserUpdate,
)

import data_manager
import ai_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for symbol_data in SYMBOL_CATALOG:
            if db.get(dm.Symbol, symbol_data["symbol_id"]) is None:
                db.add(dm.Symbol(**symbol_data))
        db.commit()
    yield

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ------ Users ------
@app.get(
    "/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def list_users(db: Annotated[Session, Depends(get_db)]):
    """
    Returns all user profiles
    """
    return db.scalars(select(dm.User)).all()


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Creates a user profile.
    :param user:
    :param db:
    :return: new_user (User)
    """
    result = db.execute(
        select(dm.User).where(dm.User.name == user.name)
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    new_user = dm.User(
        name=user.name,
        age_band=user.age_band,
        prompt_display=user.prompt_display,
        starting_format=user.starting_format,
        locations=user.locations,
        communication_goals=user.communication_goals,
        card_size=user.card_size,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
        user_id: int,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Returns a user profile by user_id.
    :param user_id:
    :param db:
    :return: user (User)
    """
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@app.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def user_update(
        user_id: int,
        user_data: UserUpdate,
        db: Annotated[Session, Depends(get_db)]
):
    """
    Updates a user's profile information.
    :param user_id:
    :param user_data: UserUpdate
    :return: User
    """
    current_info = db.get(dm.User, user_id)

    if current_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Drop unset fields
    update_data = user_data.model_dump(exclude_unset=True)
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile fields cannot be null."
        )

    if "name" in update_data:
        duplicate = db.scalar(
            select(dm.User).where(
                dm.User.name == update_data["name"],
                dm.User.user_id != user_id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

    for field, value in update_data.items():
        setattr(current_info, field, value)

    db.commit()
    db.refresh(current_info)
    return current_info


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
        user_id: int,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Deletes a user profile by user_id.
    """
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete associated records
    db.execute(
        delete(dm.UserSymbol).where(dm.UserSymbol.user_id == user_id)
    )
    db.execute(
        delete(dm.PracticeSession).where(dm.PracticeSession.user_id == user_id)
    )

    # Delete profile
    db.delete(user)
    db.commit()


# ------ Symbols ------
@app.get(
    "/symbols",
    response_model=list[SymbolResponse],
    status_code=status.HTTP_200_OK,
)
def display_symbols(db: Annotated[Session, Depends(get_db)]):
    """
    Displays all symbols
    """
    return db.scalars(select(dm.Symbol).order_by(dm.Symbol.symbol_id)).all()


@app.get("/symbols/{symbol_id}", include_in_schema=False)
def display_symbol():
    """
    Displays the selected symbol.
    """
    pass


@app.post("/symbols", include_in_schema=False)
def add_symbol():
    """
    Adds custom symbols to the Symbol table and vocab_symbol.
    """
    pass


# ------ Vocabulary ------
@app.get(
    "/vocabulary/{user_id}",
    response_model=list[UserSymbolResponse],
    status_code=status.HTTP_200_OK,
)
def display_user_vocabulary(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Displays the user's vocabulary.
    - Edit/delete symbols?
    - Custom upload button
    """
    if db.get(dm.User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    available_vocabulary = data_manager.get_user_vocabulary(db, user_id)
    return available_vocabulary


@app.post("/vocabulary/{user_id}", response_model=UserSymbolBase)
def update_vocabulary(
        user_id: int, symbol_id: int, page: str,
        db: Annotated[Session, Depends(get_db)]
):
    """
    Updates a user's vocabulary with custom upload,
    selection from the database, or AI-suggested word.
    """
    if db.get(dm.User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if db.get(dm.Symbol, symbol_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symbol is not in the database",
        )

    if db.get(dm.UserSymbol, (user_id, symbol_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Symbol is already in the vocabulary"
        )

    updated_symbol = data_manager.update_user_vocabulary(db, user_id, symbol_id, page)
    return updated_symbol


@app.delete(
    "/vocabulary/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_symbol_from_vocabulary(
        user_id: int,
        symbol_id: int,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Deletes a symbol from a user's vocabulary
    """
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    word_to_remove = db.get(dm.UserSymbol, (user_id, symbol_id))
    if word_to_remove is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word is not in the vocabulary"
        )

    # Delete profile
    db.delete(word_to_remove)
    db.commit()


@app.get("/vocabulary/{user_id}/suggestions", include_in_schema=False)
def user_vocabulary():
    """
    Displays AI-suggested words and rationale
    - Option to add to vocab, ignore or skip
    """
    pass


# ------ Practice sessions ------
@app.post("/sessions", response_model=PracticeSessionResponse)
def start_session(
    start_practice_session: StartPracticeSession,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Starts a practice session
    - Scoped to the user's vocabulary and learning phase
    :type start_practice_session: StartPracticeSession
    """
    user = db.get(dm.User, start_practice_session.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    communication_goal = start_practice_session.communication_goal
    practice_format = start_practice_session.practice_format

    # Check the goal and format is enabled in user profile
    if communication_goal not in user.communication_goals:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Requested communication goal is not enabled in user's profile",
        )

    if practice_format != user.starting_format:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Requested session format is not selected in user's profile",
        )

    # Check if location is set, otherwise use random location or none
    if start_practice_session.location is not None:
        if start_practice_session.location not in user.locations:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Requested location is not saved in user's profile",
            )
        location = start_practice_session.location
    elif user.locations:
        location = random.choice(user.locations)
    else:
        location = None

    # Get user's available vocabulary
    available_vocabulary = data_manager.get_user_vocabulary(
        db, start_practice_session.user_id
    )

    if len(available_vocabulary) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No vocabulary found for this user",
        )

    # ------ Call Question generator ------
    # pass communication_goal, practice_format, location,
    # available_vocabulary, age_band
    try:
        generated_batch: GeneratedQuestionBatch = ai_service.generate_questions(
            communication_goal,
            practice_format,
            location,
            user.age_band,
            available_vocabulary,
        )
    except (
        ai_service.LLMConfigurationError,
        ai_service.LLMProviderError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Question generation is temporarily unavailable. Please try again.",
        ) from None

    scenario = {
        "location": location,
        "questions": [
            question.model_dump(mode="json") for question in generated_batch.questions
        ],
    }

    practice_session = dm.PracticeSession(
        user_id=start_practice_session.user_id,
        communication_goal=communication_goal,
        practice_format=practice_format,
        scenario=scenario,
        session_status="active",
    )

    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)

    return practice_session


@app.post("/sessions/{session_id}/scenario", include_in_schema=False)
def generate_scenario():
    """
    LLM generates a scenario
    """
    pass


@app.post("/sessions/{session_id}/attempt")
def user_attempt():
    """
    Stores the user's attempt in a variable. All attempts are later
    summarised by AI and saved as a report.
    """
    session_responses = []


@app.post("/sessions/{session_id}/complete", include_in_schema=False)
def end_session():
    """
    Ends the practice session
    - update progression
    """
    pass


@app.get("/users/{user_id}/progression", include_in_schema=False)
def show_progression():
    """
    Displays the user's progress information
    """
    pass


@app.get("/users/{user_id}/reports", include_in_schema=False)
def show_reports():
    """
    Displays the user's reports
    """
    pass
