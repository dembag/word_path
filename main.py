import random
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Annotated

import ai_service
import data_manager
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
    VocabularyReorder,
)
from data_manager import Base, engine, get_db
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps, UnidentifiedImageError
from scripts.render_card import CardRenderer
from sqlalchemy import delete, desc, inspect, select, text
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Adds owner_user_id to database so custom symbols can be owned by a user.
    """
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        symbol_columns = {column["name"] for column in inspect(connection).get_columns("symbols")}
        if "owner_user_id" not in symbol_columns:
            connection.execute(text(
                "ALTER TABLE symbols ADD COLUMN owner_user_id INTEGER "
                "REFERENCES users(user_id) ON DELETE CASCADE"
            ))
    yield

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def static_symbol_url(image_reference: str) -> str:
    """
    Normalize a static asset reference and resolve its file metadata for cache
    busting. Path separators are standardized, leading separators are ignored, and
    an existing static prefix is removed before the asset is looked up beneath the
    configured static directory.

    :param image_reference: Static asset reference to normalize.
    :return: Static URL containing the normalized asset path and a version query
        value based on the file modification timestamp, or ``0`` when the file is
        not present.
    :raises OSError: If file metadata cannot be read after the asset is detected.
    """
    normalized = image_reference.replace("\\", "/").lstrip("/")
    normalized = normalized.removeprefix("static/")
    image_path = BASE_DIR / "static" / normalized
    version = image_path.stat().st_mtime_ns if image_path.is_file() else 0
    return f"/static/{normalized}?v={version}"


session_answers: dict[int, list[dict]] = {}


# ------ Browser interface ------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def profile_splash(request: Request, db: Annotated[Session, Depends(get_db)]):
    """
    Render the profile selection splash page for the application.

    The page prepares the data needed by the home template so visitors can choose
    from available profiles. The route configuration excludes this endpoint from
    the generated API schema.

    :param request: Incoming HTTP request used by the template response.
    :param db: Database session dependency used to load profile records.
    :return: Template response for the profile selection page.
    """
    users = db.scalars(select(dm.User).order_by(dm.User.name)).all()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"title": "Choose a profile", "users": users},
    )


@app.get("/profiles/new", response_class=HTMLResponse, include_in_schema=False)
def new_profile_page(request: Request):
    """
    Render the page used to create a new learner profile.

    Builds the template response for the profile creation form and supplies the
    template context required to populate page metadata and selectable form options,
    including age bands, response formats, prompt display modes, communication goals,
    and card sizes.

    :param request: Incoming HTTP request used by the template renderer to build the
        response context.
    :return: Rendered profile creation page response.
    :rtype: TemplateResponse
    """
    return templates.TemplateResponse(
        request=request,
        name="add_profile.html",
        context={
            "title": "Add a learner",
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


@app.get("/profiles/{user_id}", response_class=HTMLResponse, include_in_schema=False)
def profile_pre_session(
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Render the pre-session practice setup profile page.

    Builds the data needed by the pre-session template for a profile page and
    delegates rendering to the configured template engine. The response is intended
    for direct HTML delivery and is excluded from the generated API schema.

    :param user_id: Identifier of the profile owner whose practice setup page is
        requested.
    :param request: Incoming HTTP request associated with the page render.
    :param db: Database session used to load profile data.
    :raises HTTPException: If no user exists for the requested identifier.
    :return: Rendered pre-session profile page response.
    :rtype: TemplateResponse
    """
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
    """
    Render the settings page for a profile that exists in the database.

    The generated page is populated with the profile information and the
    available settings choices used by the template to display configurable
    communication, presentation, and card layout preferences.

    :param user_id: Identifier of the profile whose settings page is requested.
    :param request: Incoming web request used to build the template response.
    :param db: Database session used to load the profile.
    :raises HTTPException: If the requested profile cannot be found.
    :return: Template response containing the rendered profile settings page.
    :rtype: TemplateResponse
    """
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


@app.get("/profiles/{user_id}/vocabulary", response_class=HTMLResponse, include_in_schema=False)
def profile_vocabulary_page(
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Render the vocabulary management page for a specific user.

    Loads the requested user, retrieves the user's vocabulary entries, resolves each
    entry to its symbol data, and prepares the template context used to display the
    vocabulary manager page. Each vocabulary item is enriched with display metadata,
    including its symbol image URL and whether the symbol belongs to the requested
    user.

    :param user_id: Identifier of the user whose vocabulary is displayed.
    :param request: Incoming request used to render the template response.
    :param db: Database session used to retrieve the user, vocabulary entries, and
        related symbols.
    :raises HTTPException: If the requested user cannot be found.
    :return: Template response for the vocabulary manager page.
    :rtype: TemplateResponse
    """
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    vocabulary = data_manager.get_user_vocabulary(db, user_id)
    symbols = []
    for item in vocabulary:
        symbol = db.get(dm.Symbol, item.symbol_id)
        symbols.append({
            "symbol_id": item.symbol_id,
            "word": item.word,
            "word_class": item.word_class,
            "page": item.page,
            "position": item.position,
            "image_url": static_symbol_url(symbol.image_reference),
            "custom": symbol.owner_user_id == user_id,
        })
    return templates.TemplateResponse(
        request=request,
        name="vocabulary_manager.html",
        context={"title": f"Vocabulary for {user.name}", "user": user, "vocabulary": symbols},
    )


@app.get("/practice/{session_id}", response_class=HTMLResponse, include_in_schema=False)
def practice_page(
    session_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Render the learner practice interface by assembling the current practice
    session, resolving symbol data for questions, preparing vocabulary board
    pages, and building the template context used by the page.

    :param session_id: Identifier of the practice session to display.
    :param request: Incoming web request used to render the template response.
    :param db: Database session used to load practice, learner, symbol, and
        vocabulary records.
    :return: Rendered practice page template response.
    :rtype: TemplateResponse
    :raises HTTPException: If the practice session or learner profile cannot be
        found.
    """
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
    Retrieve user records for the users endpoint.

    The endpoint queries persistent storage through the provided database session
    and delegates response serialization to the configured response model.

    :param db: Database session dependency used to execute the user selection query.
    :return: Collection of users retrieved from persistent storage.
    :rtype: list[UserResponse]
    """
    return db.scalars(select(dm.User)).all()


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Create a user record after ensuring the requested username is available.

    The operation checks for an existing user with the same name, persists the
    validated user data, commits the transaction, and refreshes the stored record.

    :param user: User creation data containing the requested account details.
    :param db: Database session used to check uniqueness and persist the record.
    :raises HTTPException: If the requested username already exists.
    :return: The newly created user record after persistence and refresh.
    :rtype: dm.User
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
    Handle the user retrieval endpoint for the application API.

    The operation performs a database-backed lookup for a user resource and applies
    the endpoint's configured success and failure semantics through FastAPI
    response handling.

    :param user_id: Unique identifier used to locate the user.
    :param db: Database session dependency used to access persisted user records.
    :return: User record matching the requested identifier.
    :raises HTTPException: If the requested user cannot be found.
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
    Update an existing user resource with the provided partial profile data.

    Applies only fields that were explicitly supplied, rejects null values for
    provided fields, verifies that a changed username remains unique, persists the
    updated record, and returns the refreshed user representation.

    :param user_id: Identifier of the user resource to update.
    :param user_data: Partial user data containing the fields to update.
    :param db: Database session used to load, validate, persist, and refresh the
        user record.
    :raises HTTPException: If the user does not exist, if any provided field value
        is null, or if the requested username is already used by another user.
    :return: Updated and refreshed user record.
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
    Delete a user and remove records and files that depend on that user.

    Removes associated user-symbol links, practice sessions, custom symbols, and
    custom symbol image files before deleting the user record and committing the
    transaction.

    :param user_id: Identifier of the user to delete.
    :param db: Database session used to load, delete, and commit records.
    :raises HTTPException: Raised when the user does not exist.
    :return: No content is returned.
    :rtype: None
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
    custom_symbols = db.scalars(
        select(dm.Symbol).where(dm.Symbol.owner_user_id == user_id)
    ).all()
    for symbol in custom_symbols:
        (BASE_DIR / "static" / symbol.image_reference).unlink(missing_ok=True)
        db.delete(symbol)

    # Delete profile
    db.delete(user)
    db.commit()


# ------ Symbols ------
@app.get("/symbols", response_model=list[SymbolResponse], status_code=status.HTTP_200_OK)
def display_symbols(
    db: Annotated[Session, Depends(get_db)],
    user_id: int | None = Query(default=None),
):
    """
    Handle the symbol collection endpoint.

    Builds the query used to collect symbols available to clients, including the
    shared symbol set and any applicable user-scoped symbol set. Results are ordered
    deterministically by word and symbol identifier so repeated requests produce a
    stable sequence.

    :param db: Database session dependency used to query users and symbols.
    :param user_id: Optional user identifier used to include user-owned symbols.
    :raises HTTPException: If ``user_id`` is provided and no matching user exists.
    :return: Symbols matching the requested visibility scope.
    :rtype: list[SymbolResponse]
    """
    statement = select(dm.Symbol).where(dm.Symbol.owner_user_id.is_(None))
    if user_id is not None:
        if db.get(dm.User, user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        statement = select(dm.Symbol).where(
            (dm.Symbol.owner_user_id.is_(None)) | (dm.Symbol.owner_user_id == user_id)
        )
    return db.scalars(statement.order_by(dm.Symbol.word, dm.Symbol.symbol_id)).all()


@app.post("/symbols/custom", response_model=SymbolResponse, status_code=status.HTTP_201_CREATED)
def add_custom_symbol(
    user_id: int = Form(...),
    word: str = Form(...),
    page: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Create a custom symbol from an uploaded image, render it as a symbol card, store
    the generated image, persist the symbol record, and add it to the selected user
    vocabulary page.

    :param user_id: Identifier of the user who owns the custom symbol.
    :param word: Label to display on the generated symbol card.
    :param page: Vocabulary page that should receive the new symbol.
    :param image: Uploaded image file used as the symbol artwork.
    :param db: Database session used to read, create, and update records.
    :return: Created custom symbol record.
    :raises HTTPException: If the user is not found, submitted data is invalid, the
        image is too large, or the uploaded file is not a supported image.
    """
    user = db.get(dm.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    word = word.strip()
    if not word or len(word) > 20:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Word label must be 1 to 20 characters.")
    if page not in {"personal", "core", "general"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Choose Personal, Core, or General.")

    contents = image.file.read(5 * 1024 * 1024 + 1)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 5 MB or smaller.")
    try:
        with Image.open(BytesIO(contents)) as source_image:
            if source_image.format not in {"PNG", "JPEG", "WEBP"}:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Upload a PNG, JPEG, or WebP image.")
            if source_image.width * source_image.height > 25_000_000:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image dimensions must be 25 megapixels or smaller.")
            source_image.verify()
        with Image.open(BytesIO(contents)) as source_image:
            converted = ImageOps.exif_transpose(source_image)
            converted.thumbnail((1200, 1200))
            converted = converted.convert("RGBA" if "A" in converted.getbands() else "RGB")
            rendered_card = CardRenderer().render(converted, word)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="The uploaded file is not a supported image.")

    image_directory = BASE_DIR / "static" / "custom_symbols" / str(user_id)
    image_directory.mkdir(parents=True, exist_ok=True)
    image_name = f"{uuid.uuid4().hex}_card.png"
    image_path = image_directory / image_name
    rendered_card.save(image_path, format="PNG")
    symbol = dm.Symbol(
        word=word,
        word_class="custom",
        image_reference=f"custom_symbols/{user_id}/{image_name}",
        source="custom_upload",
        owner_user_id=user_id,
    )
    try:
        db.add(symbol)
        db.flush()
        data_manager.update_user_vocabulary(db, user_id, symbol.symbol_id, page)
    except Exception:
        db.rollback()
        image_path.unlink(missing_ok=True)
        raise
    return symbol


# ------ Vocabulary ------
@app.get(
    "/vocabulary/{user_id}",
    response_model=list[UserSymbolResponse],
    status_code=status.HTTP_200_OK,
)
def display_user_vocabulary(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Display the vocabulary associated with a user through the vocabulary endpoint.

    The function checks that the requested user exists and then retrieves the
    vocabulary entries available to that user from the database-backed data layer.

    :param user_id: Identifier of the user whose vocabulary is requested.
    :param db: Database session dependency used to access stored user and
        vocabulary data.
    :raises HTTPException: If no user exists for the supplied identifier.
    :return: Vocabulary entries available for the user.
    :rtype: list[UserSymbolResponse]
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
    Add an accessible symbol to a learner's vocabulary for the requested
    vocabulary page.

    The operation validates that the learner and symbol exist, that the requested
    page is supported, that the symbol is available to the learner, and that the
    symbol is not already present in the learner's vocabulary before persisting the
    update.

    :param user_id: Identifier of the learner whose vocabulary is being updated.
    :param symbol_id: Identifier of the symbol to add to the learner's vocabulary.
    :param page: Vocabulary page where the symbol should be added.
    :param db: Database session used to read and persist vocabulary data.
    :raises HTTPException: If the learner does not exist, the symbol does not
        exist, the page is unsupported, the symbol is unavailable to the learner,
        or the symbol is already in the learner's vocabulary.
    :return: Updated learner-symbol vocabulary association.
    :rtype: UserSymbolBase
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

    if page not in {"personal", "core", "general"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Choose Personal, Core, or General.")

    symbol = db.get(dm.Symbol, symbol_id)
    if symbol.owner_user_id is not None and symbol.owner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol is not available to this learner")

    if db.get(dm.UserSymbol, (user_id, symbol_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Symbol is already in the vocabulary"
        )

    updated_symbol = data_manager.update_user_vocabulary(db, user_id, symbol_id, page)
    return updated_symbol


@app.put("/vocabulary/{user_id}/order", status_code=status.HTTP_204_NO_CONTENT)
def reorder_user_vocabulary(
    user_id: int,
    order: VocabularyReorder,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Reorders assigned vocabulary symbols by validating the submitted ordering and
    persisting updated section and position data.

    :param user_id: Identifier of the user whose vocabulary order is being updated.
    :param order: Submitted vocabulary section ordering to apply.
    :param db: Database session used to load and update user vocabulary records.
    :raises HTTPException: If the user does not exist.
    :raises HTTPException: If the submitted order does not include every assigned
        symbol exactly once.
    :return: None.
    :rtype: None
    """
    if db.get(dm.User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    current = db.scalars(select(dm.UserSymbol).where(dm.UserSymbol.user_id == user_id)).all()
    submitted_ids = [symbol_id for ids in order.sections.values() for symbol_id in ids]
    if len(submitted_ids) != len(set(submitted_ids)) or set(submitted_ids) != {row.symbol_id for row in current}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Order must include every assigned symbol exactly once.")
    symbols_by_id = {row.symbol_id: row for row in current}
    for page in ("personal", "core", "general"):
        for position, symbol_id in enumerate(order.sections.get(page, []), start=1):
            symbols_by_id[symbol_id].page = page
            symbols_by_id[symbol_id].position = position
    db.commit()


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
    Remove a symbol from a user's vocabulary.

    Validates that the requested user exists and that the specified symbol is
    currently associated with the user's vocabulary. If both records are found, the
    vocabulary entry is deleted and the change is committed to the database.

    :param user_id: Identifier of the user whose vocabulary entry should be
        removed.
    :param symbol_id: Identifier of the symbol to remove from the user's
        vocabulary.
    :param db: Database session used to retrieve, delete, and commit the
        vocabulary entry.
    :raises HTTPException: If the user does not exist or the symbol is not present
        in the user's vocabulary.
    :return: No content is returned after successful deletion.
    :rtype: None
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


# ------ Practice sessions ------
@app.post("/sessions", response_model=PracticeSessionStartResponse)
def start_session(
    start_practice_session: StartPracticeSession,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Start a practice session by validating the requested profile configuration,
    selecting an applicable scenario location, generating practice questions from
    the available vocabulary, and persisting the active session state.

    :param start_practice_session: Practice session start request containing the
        selected user, communication goal, practice format, and optional location.
    :param db: Database session dependency used to load profile data, retrieve
        vocabulary, and persist the created practice session.
    :raises HTTPException: Raised with a not-found status when the user does not
        exist, with an unprocessable-entity status when the requested goal, format,
        location, or vocabulary state is invalid, or with a service-unavailable
        status when question generation cannot be completed.
    :return: Created practice session response data, including session identifiers,
        selected configuration, generated questions, status, summary, and
        timestamps.
    :rtype: dict[str, object]
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
            db,
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
    Records an answer attempt for an active practice session.

    Validates that the requested practice session exists, accepts answers, includes
    the submitted question, and receives timezone-aware prompt timestamps in the
    required chronological order. Determines the response support level, stores the
    answer event for the session, and returns confirmation details for the recorded
    attempt.

    :param session_id: Identifier of the practice session that receives the answer.
    :param answer: Submitted answer payload containing the question, selected
        symbols, and prompt timing information.
    :param db: Database session dependency used to load the practice session.
    :raises HTTPException: If the practice session cannot be found.
    :raises HTTPException: If the practice session is not active.
    :raises HTTPException: If the submitted question is not part of the session.
    :raises HTTPException: If any supplied timestamp does not include timezone
        information.
    :raises HTTPException: If prompt timestamps are not in the required
        chronological order.
    :return: Confirmation data containing the session identifier, question
        identifier, response order, and recorded status.
    :rtype: dict[str, int | bool]
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
    Complete a practice session and produce its final response payload.

    Finalizes a practice session by validating that it exists and has not already
    been completed, scoring submitted answers, calculating accuracy and prompting
    independence metrics, storing per-question summary data, and marking the
    session as completed. After persisting the completion summary, the function
    attempts to generate a review and records whether that review is available.
    Submitted in-memory answer data for the session is cleared after the initial
    summary is committed.

    :param session_id: Identifier of the practice session to complete.
    :param db: Database session used to load, update, commit, and refresh the
        practice session and related symbol records.
    :raises HTTPException: If the practice session cannot be found, or if it has
        already been completed.
    :return: Serialized completed practice session data, including metadata,
        completion timestamps, question data, computed summary results, and review
        availability information.
    :rtype: dict[str, object]
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
