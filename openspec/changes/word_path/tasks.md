# Tasks

## Ownership

- The learner implements most Python backend work. The assistant explains one manageable step at a time, reviews the learner's code, and helps debug before moving on.
- Keep endpoints and their request/response shapes clear enough to exercise with FastAPI's API docs or simple HTTP requests.

## 1. SQLite and model foundation

- [x] 1.1 Simplify database configuration to a local SQLite file and remove runtime dependence on PostgreSQL settings; confirm the FastAPI app can open a database session.
- [ ] 1.2 Define the MVP SQLAlchemy models: `User`, `UserSymbol`, and `PracticeSession`, with generic JSON columns only where needed; create tables from metadata at startup.
- [ ] 1.3 Align Pydantic schemas with the profile, symbol, and session data; use shared literals/validation for goals, age bands, formats, and statuses where appropriate.
- [ ] 1.4 Add a small fictional seed/demo dataset and a Python fixture containing a few fixed practice scenarios.

## 2. Learner and vocabulary endpoints

- [ ] 2.1 Implement endpoints to read and update the demo learner profile; reject invalid profile values and confirm changes are reflected in later reads.
- [ ] 2.2 Implement endpoints to list and add user symbols, including optional image reference and attribution fields; confirm newly added symbols belong to the demo learner.

## 3. Practice session endpoints

- [ ] 3.1 Implement session start using an enabled learner goal, a supported practice format, and one matching fixed scenario; reject unsupported goals or formats.
- [ ] 3.2 Implement response submission for an active session and keep response events in runtime memory only; reject responses to missing or completed sessions.
- [ ] 3.3 Implement session completion, calculate a small summary, persist it on `PracticeSession`, and clear transient response data.

## 4. MVP walkthrough

- [ ] 4.1 Walk through profile read/update, symbol list/add, session start, response, and completion using fictional data and the API docs or simple HTTP requests.
- [ ] 4.2 Update the basic setup notes to explain running the SQLite app and exercising the endpoints; remove instructions that require Docker, PostgreSQL, or Alembic for the MVP.
- [ ] 4.3 Review the change against the mentor's MVP scope and identify any deferred capability that is still required by the course before expanding implementation.
