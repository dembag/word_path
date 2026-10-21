# Tasks

## Ownership

- The learner implements most Python backend work. The assistant explains one manageable step at a time, reviews the learner's code, and helps debug before moving on.
- Keep endpoints and their request/response shapes clear enough to exercise with FastAPI's API docs or simple HTTP requests.

## 1. SQLite and model foundation

- [x] 1.1 Simplify database configuration to a local SQLite file and remove runtime dependence on PostgreSQL settings; confirm the FastAPI app can open a database session.
- [x] 1.2 Define the MVP SQLAlchemy models: `User`, shared `Symbol`, `UserSymbol` association with learner-specific page/position, and `PracticeSession`, with generic JSON columns only where needed; create tables from metadata at startup.
- [x] 1.3 Align Pydantic schemas with profiles, catalog symbols, learner-symbol associations, and sessions; use shared literals/validation for goals, age bands, formats, and statuses where appropriate.
- [x] 1.4 Add a small fictional learner fixture, predefined shared catalog symbols, and a few fixed practice scenarios in `dummy_data.py`; preload catalog symbols into SQLite without inserting the learner fixture.

## 2. Learner and vocabulary endpoints

- [ ] 2.1 Implement user CRUD endpoints in SQLite; reject invalid values, confirm created/updated profiles are reflected in later reads, and cascade user deletion to their symbol associations and sessions while preserving shared catalog symbols.
- [ ] 2.2 Implement endpoints to list catalog symbols and add/remove catalog symbol associations for a learner; preserve each association's page/position and confirm operations affect only that learner's collection.

## 3. Practice session endpoints

- [ ] 3.1 Implement session start using an enabled learner goal, a supported practice format, and one matching fixed scenario; reject unsupported goals or formats.
- [ ] 3.2 Implement response submission for an active session and keep response events in runtime memory only; reject responses to missing or completed sessions.
- [ ] 3.3 Implement session completion, calculate a small summary, persist it on `PracticeSession`, and clear transient response data.

## 4. MVP walkthrough

- [ ] 4.1 Walk through user CRUD, symbol list/create/delete, session start, response, and completion using the API docs or simple HTTP requests.
- [ ] 4.2 Update the basic setup notes to explain running the SQLite app and exercising the endpoints; remove instructions that require Docker, PostgreSQL, or Alembic for the MVP.
- [ ] 4.3 Review the change against the mentor's MVP scope and identify any deferred capability that is still required by the course before expanding implementation.
