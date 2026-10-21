from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from data_manager import Base, engine, get_db, SessionLocal
from dummy_data import SYMBOL_CATALOG
import data_models as dm

from api_schemas import UserCreate, UserResponse, UserUpdate


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
@app.get("/symbols", include_in_schema=False)
def display_symbols():
    """
    Displays the symbols in the Symbols table.
    - sort/search by tags, word type
    - Custom upload option
    """
    pass


@app.get("/symbols/{symbol_id}", include_in_schema=False)
def display_symbol():
    """
    Displays the selected symbol.
    """
    pass


@app.post("/symbols", include_in_schema=False)
def add_custom_symbol():
    """
    Adds custom symbols to the Symbol table and vocab_symbol.
    """
    pass


# ------ Vocabulary ------
@app.get("/vocabulary/{user_id}", include_in_schema=False)
def user_vocabulary():
    """
    Displays the user's vocabulary.
    - Edit/delete symbols?
    - Custom upload button
    """
    pass


@app.post("/vocabulary/{user_id}", include_in_schema=False)
def update_vocabulary():
    """
    Updates a user's vocabulary with custom upload,
    selection from the database, or AI-suggested word.
    """
    pass


@app.get("/vocabulary/{user_id}/suggestions", include_in_schema=False)
def user_vocabulary():
    """
    Displays AI-suggested words and rationale
    - Option to add to vocab, ignore or skip
    """
    pass


# ------ Practice sessions ------
@app.post("/sessions", include_in_schema=False)
def start_session():
    """
    Starts a practice session
    - Scoped to the user's vocabulary and learning phase
    """
    pass


@app.post("/sessions/{session_id}/scenario", include_in_schema=False)
def generate_scenario():
    """
    LLM generates a scenario
    """
    pass


@app.post("/sessions/{session_id}/attempt", include_in_schema=False)
def user_attempt():
    """
    Submits a user's response
    """
    pass


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