import random
from datetime import datetime, UTC

from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated
from sqlalchemy import delete, select, desc
from sqlalchemy.orm import Session

from data_manager import Base, engine, get_db
import data_models as dm

from api_schemas import (
    AnswerRecorded,
    GeneratedQuestionBatch,
    PracticeSessionResponse,
    PracticeSessionStartResponse,
    StartPracticeSession,
    SubmitAnswer,
    SummaryInformation,
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
    yield

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def static_symbol_url(image_reference: str) -> str:
    """Build a static image URL that changes when the image file is updated."""
    normalized = image_reference.replace("\\", "/").lstrip("/")
    if normalized.startswith("static/"):
        normalized = normalized[len("static/"):]
    image_path = BASE_DIR / "static" / normalized
    version = image_path.stat().st_mtime_ns if image_path.is_file() else 0
    return f"/static/{normalized}?v={version}"


session_answers: dict[int, list[dict]] = {}


# ------ Browser interface ------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def profile_splash(request: Request, db: Annotated[Session, Depends(get_db)]):
    """Shows the available learner profiles."""
    users = db.scalars(select(dm.User).order_by(dm.User.name)).all()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"title": "Choose a profile", "users": users},
    )


@app.get("/profiles/{user_id}", response_class=HTMLResponse, include_in_schema=False)
def profile_pre_session(
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """Shows the selected learner's profile and practice setup."""
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    goal_labels = {
        "requesting": "Requesting",
        "sharing_information": "Sharing information",
        "social_interaction": "Social interaction",
        "communication_repair": "Communication repair",
    }
    return templates.TemplateResponse(
        request=request,
        name="pre_session.html",
        context={
            "title": f"{user.name}'s practice setup",
            "user": user,
            "goal_labels": goal_labels,
        },
    )


@app.get(
    "/profiles/{user_id}/settings",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def profile_settings_page(
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """Shows editable profile settings before practice."""
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="profile_settings.html",
        context={
            "title": f"Settings for {user.name}",
            "user": user,
            "age_bands": ["0-5", "6-9", "10-13", "14-17", "18+"],
            "formats": ["choice", "sentence"],
            "prompt_displays": ["text_only", "symbols_and_text"],
            "communication_goals": [
                ("requesting", "Requesting"),
                ("sharing_information", "Sharing information"),
                ("social_interaction", "Social interaction"),
                ("communication_repair", "Communication repair"),
            ],
            "card_sizes": ["small", "medium", "large"],
        },
    )


@app.get("/practice/{session_id}", response_class=HTMLResponse, include_in_schema=False)
def practice_page(
    session_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """Renders a practice session prompt for the selected learner."""
    practice_session = db.get(dm.PracticeSession, session_id)
    if practice_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found",
        )

    user = db.get(dm.User, practice_session.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found",
        )

    questions = practice_session.scenario.get("questions", [])
    symbol_ids = {
        symbol_id
        for question in questions
        for symbol_id in (
            question.get("question_symbol_ids", [])
            + question.get("available_symbol_ids", [])
        )
    }
    symbols = db.scalars(
        select(dm.Symbol).where(dm.Symbol.symbol_id.in_(symbol_ids))
    ).all()
    symbols_by_id = {symbol.symbol_id: symbol for symbol in symbols}

    ui_questions = []
    for question in questions:
        ui_question = dict(question)
        ui_question["question_symbols"] = []
        for symbol_id in question.get("question_symbol_ids", []):
            symbol = symbols_by_id.get(symbol_id)
            if symbol is None:
                continue
            ui_question["question_symbols"].append(
                {
                    "symbol_id": symbol.symbol_id,
                    "word": symbol.word,
                    "image_url": static_symbol_url(symbol.image_reference),
                }
            )
        ui_question["available_symbols"] = []
        for symbol_id in question.get("available_symbol_ids", []):
            symbol = symbols_by_id.get(symbol_id)
            if symbol is None:
                continue
            ui_question["available_symbols"].append(
                {
                    "symbol_id": symbol.symbol_id,
                    "word": symbol.word,
                    "image_url": static_symbol_url(symbol.image_reference),
                }
            )
        ui_questions.append(ui_question)

    vocabulary = data_manager.get_user_vocabulary(db, user.user_id)
    vocabulary_ids = [symbol.symbol_id for symbol in vocabulary]
    vocabulary_symbols = db.scalars(
        select(dm.Symbol).where(dm.Symbol.symbol_id.in_(vocabulary_ids))
    ).all()
    vocabulary_by_id = {symbol.symbol_id: symbol for symbol in vocabulary_symbols}

    board_symbols = {page: [] for page in ("personal", "core", "general")}
    for user_symbol in vocabulary:
        symbol = vocabulary_by_id.get(user_symbol.symbol_id)
        if symbol is None:
            continue
        if user_symbol.page in {"people", "personal"}:
            page = "personal"
        elif user_symbol.page == "core":
            page = "core"
        else:
            page = "general"
        board_symbol = {
            "symbol_id": symbol.symbol_id,
            "word": symbol.word,
            "word_class": symbol.word_class,
            "page": page,
            "position": user_symbol.position,
            "image_url": static_symbol_url(symbol.image_reference),
        }
        board_symbols[page].append(board_symbol)

    board_pages = [
        {
            "page": page,
            "symbols": sorted(
                symbols,
                key=lambda item: (item["position"], item["symbol_id"]),
            ),
        }
        for page, symbols in board_symbols.items()
        if symbols
    ]

    return templates.TemplateResponse(
        request=request,
        name="practice.html",
        context={
            "title": f"{user.name}'s practice session",
            "user": user,
            "practice_session": practice_session,
            "practice_questions": ui_questions,
            "board_pages": board_pages,
            "total_questions": len(ui_questions),
        },
    )


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
@app.post("/sessions", response_model=PracticeSessionStartResponse)
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

    return {
        "session_id": practice_session.session_id,
        "user_id": practice_session.user_id,
        "communication_goal": practice_session.communication_goal,
        "practice_format": practice_session.practice_format,
        "location": practice_session.scenario.get("location"),
        "session_status": practice_session.session_status,
        "summary": practice_session.summary,
        "questions": [
            question
            for question in practice_session.scenario.get("questions", [])
        ],
        "started_at": practice_session.started_at,
        "completed_at": practice_session.completed_at,
    }


@app.post("/sessions/{session_id}/attempt", response_model=AnswerRecorded)
def user_attempt(
    session_id: int,
    answer: SubmitAnswer,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Stores the user's attempt in a variable. All attempts are later
    summarised by AI and saved as a report.
    """
    current_practice_session = db.get(dm.PracticeSession, session_id)
    if current_practice_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found",
        )
    if current_practice_session.session_status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot submit an answer to a completed session",
        )

    questions = current_practice_session.scenario.get("questions", [])
    question_exists = any(
        question.get("question_id") == answer.question_id for question in questions
    )

    if not question_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this session",
        )

    presented_at = answer.question_presented_at
    verbal_at = answer.verbal_prompt_at
    modeled_at = answer.modeled_prompt_at

    timestamps = [presented_at, verbal_at, modeled_at]
    if any(
        value is not None and (value.tzinfo is None or value.utcoffset() is None)
        for value in timestamps
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Answer timestamps must include a timezone",
        )

    if verbal_at is not None and verbal_at < presented_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Verbal prompt cannot precede question presentation",
        )

    if modeled_at is not None and modeled_at < (verbal_at or presented_at):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Modeled prompt must follow question presentation and any verbal prompt",
        )

    support_level: str = (
        "modeled"
        if modeled_at is not None
        else "verbal_prompt" if verbal_at is not None else "independent"
    )
    answered_at = datetime.now(UTC)

    answers_for_session = session_answers.setdefault(session_id, [])
    event = {
        "question_id": answer.question_id,
        "answer_symbol_ids": answer.answer_symbol_ids.copy(),
        "support_level": support_level,
        "presented_at": presented_at,
        "verbal_prompt_at": verbal_at,
        "modeled_prompt_at": modeled_at,
        "answered_at": answered_at,
        "response_order": len(answers_for_session) + 1,
    }
    answers_for_session.append(event)

    return {
        "session_id": session_id,
        "question_id": answer.question_id,
        "response_order": event["response_order"],
        "recorded": True,
    }


@app.post(
    "/sessions/{session_id}/complete",
    response_model=PracticeSessionResponse,
)
def end_session(session_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Ends the practice session
    - update progression
    """
    practice_session = db.get(dm.PracticeSession, session_id)

    if practice_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session cannot be found",
        )

    if practice_session.session_status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Practice session is already completed",
        )

    session_questions = practice_session.scenario["questions"]
    attempts_by_question: dict[int, list[dict]] = {}
    for event in session_answers.get(session_id, []):
        attempts_by_question.setdefault(event["question_id"], []).append(event)

    correct_count = 0
    answered_count = 0
    independent_count = 0
    verbal_count = 0
    modeled_count = 0
    summary_data = []

    for question in session_questions:
        attempts = attempts_by_question.get(question["question_id"], [])
        if not attempts:
            continue
        # Score the first submitted response. Keep later attempts in the saved
        # question details so retries remain available in the session summary.
        event = attempts[0]

        elapsed_seconds = (event["answered_at"] - event["presented_at"]).total_seconds()
        if elapsed_seconds < 0:
            continue

        answered_count += 1
        if event["answer_symbol_ids"] == question["expected_response"]:
            correct_count += 1

        if elapsed_seconds < 10:
            independence = "independent"
            independent_count += 1
        elif elapsed_seconds < 20:
            independence = "verbal_prompt"
            verbal_count += 1
        else:
            independence = "modeled"
            modeled_count += 1

        answer_words = []
        for symbol_id in event["answer_symbol_ids"]:
            symbol = db.get(dm.Symbol, symbol_id)
            if symbol is not None:
                answer_words.append(symbol.word)

        available_words = []
        for symbol_id in question["available_symbol_ids"]:
            symbol = db.get(dm.Symbol, symbol_id)
            if symbol is not None:
                available_words.append(symbol.word)

        expected_response_words = []
        for symbol_id in question["expected_response"]:
            symbol = db.get(dm.Symbol, symbol_id)
            if symbol is not None:
                expected_response_words.append(symbol.word)

        response_attempts = []
        for attempt in attempts:
            attempt_words = []
            for symbol_id in attempt["answer_symbol_ids"]:
                symbol = db.get(dm.Symbol, symbol_id)
                if symbol is not None:
                    attempt_words.append(symbol.word)
            response_attempts.append(
                {
                    "response_ids": attempt["answer_symbol_ids"],
                    "response_words": attempt_words,
                }
            )

        summary_data.append(
            {
                "question_id": question["question_id"],
                "question": question["question"],
                "available_ids": question["available_symbol_ids"],
                "available_words": available_words,
                "expected_response_ids": question["expected_response"],
                "expected_response_words": expected_response_words,
                "response_ids": event["answer_symbol_ids"],
                "response_words": answer_words,
                "correct": event["answer_symbol_ids"] == question["expected_response"],
                "independence": independence,
                "attempt_count": len(attempts),
                "response_attempts": response_attempts,
            }
        )

    correct_percent = (correct_count / answered_count) * 100 if answered_count else None
    independent_percent = (
        (independent_count / answered_count) * 100 if answered_count else None
    )
    verbal_percent = (verbal_count / answered_count) * 100 if answered_count else None
    modeled_percent = (modeled_count / answered_count) * 100 if answered_count else None

    practice_session.summary = {
        "results": {
            "total_questions": len(session_questions),
            "answered_count": answered_count,
            "correct_count": correct_count,
            "accuracy": correct_percent,
            "independent": independent_percent,
            "verbal_prompt": verbal_percent,
            "modeled": modeled_percent,
        },
        "question_results": summary_data,
        "unanswered_questions": [
            {
                "question_id": question["question_id"],
                "question": question["question"],
            }
            for question in session_questions
            if question["question_id"] not in attempts_by_question
        ],
    }

    # Update the database
    practice_session.session_status = "completed"
    practice_session.completed_at = datetime.now(UTC)

    db.commit()
    db.refresh(practice_session)

    session_answers.pop(session_id, None)

    # Generate the review
    review = None
    review_status = "unavailable"

    summary_information = SummaryInformation(
        communication_goal=practice_session.communication_goal,
        practice_format=practice_session.practice_format,
        location=practice_session.scenario.get("location"),
        results=practice_session.summary["results"],
        question_results=practice_session.summary["question_results"],
    )

    try:
        generated_review = ai_service.generate_review(summary_information)
    except (
        ai_service.LLMConfigurationError,
        ai_service.LLMProviderError,
        ValueError,
    ):
        pass
    else:
        review = generated_review.review
        review_status = "available"

    practice_session.summary = {
        **practice_session.summary,
        "review": review,
        "review_status": review_status,
    }
    db.commit()
    db.refresh(practice_session)


    return {
        "session_id": practice_session.session_id,
        "user_id": practice_session.user_id,
        "communication_goal": practice_session.communication_goal,
        "practice_format": practice_session.practice_format,
        "location": practice_session.scenario.get("location"),
        "session_status": practice_session.session_status,
        "summary": practice_session.summary,
        "questions": [
            {
                key: value
                for key, value in question.items()
                if key != "expected_response"
            }
            for question in practice_session.scenario.get("questions", [])
        ],
        "started_at": practice_session.started_at,
        "completed_at": practice_session.completed_at,
    }


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
