from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pathlib import Path

from api_schemas import UserCreate, UserResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

users = [
    {
        "user_id": 1,
        "name": "Liam",
        "date_of_birth": "2015-12-09",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 1",
        "ai_can_add_vocab": False,
        "created_at": "2026-01-12 12:00:00"
    },
    {
        "user_id": 2,
        "name": "Emma",
        "date_of_birth": "2020-02-22",
        "vocab_tier": "extended",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-01-19 17:00:00"
    },
    {
        "user_id": 3,
        "name": "Noah",
        "date_of_birth": "2019-07-02",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 1",
        "ai_can_add_vocab": True,
        "created_at": "2026-01-26 10:00:00"
    },
    {
        "user_id": 4,
        "name": "Mia",
        "date_of_birth": "2016-09-20",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-02-02 17:00:00"
    },
    {
        "user_id": 5,
        "name": "Oliver",
        "date_of_birth": "2020-11-23",
        "vocab_tier": "extended",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-02-09 15:00:00"
    },
    {
        "user_id": 6,
        "name": "Sophie",
        "date_of_birth": "2018-10-09",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": True,
        "created_at": "2026-02-16 11:00:00"
    },
    {
        "user_id": 7,
        "name": "Elias",
        "date_of_birth": "2017-05-05",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 4",
        "ai_can_add_vocab": False,
        "created_at": "2026-02-23 14:00:00"
    },
    {
        "user_id": 8,
        "name": "Hannah",
        "date_of_birth": "2015-07-04",
        "vocab_tier": "core",
        "pecs_phase": "Phase 1",
        "ai_can_add_vocab": False,
        "created_at": "2026-03-02 14:00:00"
    },
    {
        "user_id": 9,
        "name": "Leo",
        "date_of_birth": "2017-01-24",
        "vocab_tier": "core",
        "pecs_phase": "Phase 5",
        "ai_can_add_vocab": True,
        "created_at": "2026-03-09 17:00:00"
    },
    {
        "user_id": 10,
        "name": "Lena",
        "date_of_birth": "2018-02-18",
        "vocab_tier": "core",
        "pecs_phase": "Phase 1",
        "ai_can_add_vocab": False,
        "created_at": "2026-03-16 14:00:00"
    },
    {
        "user_id": 11,
        "name": "Finn",
        "date_of_birth": "2016-12-03",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 5",
        "ai_can_add_vocab": False,
        "created_at": "2026-03-23 12:00:00"
    },
    {
        "user_id": 12,
        "name": "Clara",
        "date_of_birth": "2015-04-28",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 3",
        "ai_can_add_vocab": True,
        "created_at": "2026-03-30 15:00:00"
    },
    {
        "user_id": 13,
        "name": "Jonas",
        "date_of_birth": "2018-11-27",
        "vocab_tier": "core",
        "pecs_phase": "Phase 3",
        "ai_can_add_vocab": False,
        "created_at": "2026-04-06 11:00:00"
    },
    {
        "user_id": 14,
        "name": "Ella",
        "date_of_birth": "2017-04-22",
        "vocab_tier": "core",
        "pecs_phase": "Phase 3",
        "ai_can_add_vocab": False,
        "created_at": "2026-04-13 10:00:00"
    },
    {
        "user_id": 15,
        "name": "Ben",
        "date_of_birth": "2020-03-18",
        "vocab_tier": "extended",
        "pecs_phase": "Phase 5",
        "ai_can_add_vocab": True,
        "created_at": "2026-04-20 12:00:00"
    },
    {
        "user_id": 16,
        "name": "Nora",
        "date_of_birth": "2018-07-09",
        "vocab_tier": "extended",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-04-27 17:00:00"
    },
    {
        "user_id": 17,
        "name": "Luca",
        "date_of_birth": "2020-06-27",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-05-04 12:00:00"
    },
    {
        "user_id": 18,
        "name": "Amelie",
        "date_of_birth": "2021-06-13",
        "vocab_tier": "core",
        "pecs_phase": "Phase 1",
        "ai_can_add_vocab": True,
        "created_at": "2026-05-11 10:00:00"
    },
    {
        "user_id": 19,
        "name": "Paul",
        "date_of_birth": "2019-12-11",
        "vocab_tier": "starter",
        "pecs_phase": "Phase 2",
        "ai_can_add_vocab": False,
        "created_at": "2026-05-18 16:00:00"
    },
    {
        "user_id": 20,
        "name": "Ida",
        "date_of_birth": "2020-08-05",
        "vocab_tier": "core",
        "pecs_phase": "Phase 4",
        "ai_can_add_vocab": False,
        "created_at": "2026-05-25 11:00:00"
    }
]


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