from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager

from data_manager import Base, engine
import data_models

from api_schemas import UserCreate, UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")



# ------ Users ------
@app.get("/")
@app.get("/users")
def home(request: Request):
    """
    Displays all users.
    - Add/delete user buttons?
    """
    return templates.TemplateResponse(
        request, "home.html", {"users": users, "title": "Custom Title"}
    )


@app.get("/users/{user_id}")
def user_profile(user_id: int):
    """
    Displays editable profile fields and settings.
    - Card size
    - AI can add vocab
    - Custom symbol upload option
    """
    for user in users:
        if user.get("user_id") == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.post("/users/{user_id")
def update_profile():
    """
    Updates the user's profile.
    """
    pass


# ------ Symbols ------
@app.get("/symbols")
def display_symbols():
    """
    Displays the symbols in the Symbols table.
    - sort/search by tags, word type
    - Custom upload option
    """
    pass


@app.get("/symbols/{symbol_id}")
def display_symbol():
    """
    Displays the selected symbol.
    """
    pass


@app.post("/symbols")
def add_custom_symbol():
    """
    Adds custom symbols to the Symbol table and vocab_symbol.
    """
    pass


# ------ Vocabulary ------
@app.get("/vocabulary/{user_id}")
def user_vocabulary():
    """
    Displays the user's vocabulary.
    - Edit/delete symbols?
    - Custom upload button
    """
    pass


@app.post("/vocabulary/{user_id}")
def update_vocabulary():
    """
    Updates a user's vocabulary with custom upload,
    selection from the database, or AI-suggested word.
    """
    pass


@app.get("/vocabulary/{user_id}/suggestions")
def user_vocabulary():
    """
    Displays AI-suggested words and rationale
    - Option to add to vocab, ignore or skip
    """
    pass


# ------ Practice sessions ------
@app.post("/sessions")
def start_session():
    """
    Starts a practice session
    - Scoped to the user's vocabulary and learning phase
    """
    pass


@app.post("/sessions/{session_id}/scenario")
def generate_scenario():
    """
    LLM generates a scenario
    """
    pass


@app.post("/sessions/{session_id}/attempt")
def user_attempt():
    """
    Submits a user's response
    """
    pass


@app.post("/sessions/{session_id}/complete")
def end_session():
    """
    Ends the practice session
    - update progression
    """
    pass


@app.get("/users/{user_id}/progression")
def show_progression():
    """
    Displays the user's progress information
    """
    pass


@app.get("/users/{user_id}/reports")
def show_reports():
    """
    Displays the user's reports
    """
    pass