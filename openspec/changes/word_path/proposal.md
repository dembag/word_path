# Proposal

## Why

The current project is a small FastAPI application, and the mentor advised keeping the MVP backend simple. A working SQLite-backed API with a little dummy data will make it possible to demonstrate the main flow before adding external services or infrastructure.

## What Changes

- Build the first backend slice around a learner profile, the learner's vocabulary symbols, and practice sessions.
- Use SQLite and SQLAlchemy for local persistence, with Pydantic schemas for API input and output.
- Provide a small set of endpoints to read and update a learner, list and add vocabulary symbols, and start, respond to, and complete a practice session.
- Use a few fixed scenarios from a Python data file so the endpoints can be exercised without an AI service.
- Keep learner responses in memory while a session is active and persist a short session summary when it is completed.
- Keep API routes and model behavior small enough for the learner to implement and explain; guide backend implementation one manageable step at a time.

## Capabilities

### New Capabilities

- `aac-practice`: A basic practice-session flow using fixed scenarios and a saved completion summary.
- `learner-vocabulary`: A learner profile and learner-owned vocabulary symbols, including basic image source and attribution details where available.

### Deferred Capabilities

- `aac-guidance-retrieval`, AI-generated scenarios or recommendations, ARASAAC search/import, caregiver review pages, and richer analytics are later work. They are not required for this first backend slice.

## Impact

- Simplify the existing FastAPI routes, SQLAlchemy models, database configuration, and Pydantic schemas to support the agreed MVP flow.
- Use SQLite locally and avoid adding Docker, PostgreSQL, Alembic migrations, or pgvector for this stage.
- Add a small Python module containing dummy practice scenarios and, if useful, seed a demo learner and a few vocabulary symbols.
- Keep demo data fictional and avoid storing individual response events after session completion.
- Reconcile the longer-term capability specs with this reduced MVP before treating the full change as complete.
