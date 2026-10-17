# Design

## Context

This is a course MVP for a small FastAPI app. The mentor's guidance is to focus on backend endpoints and demonstrate the flow with dummy data, using SQLite and avoiding infrastructure work that does not help the first demonstration.

## Goals / Non-Goals

**Goals:**

- Provide a simple API flow to create learner profiles and practise communication goals.
- Persist created learner profiles, learner vocabulary, and completed session summaries in SQLite.
- Use fixed dummy scenarios so the flow works without network access or model credentials.
- Keep the implementation approachable and explainable as the learner writes most of the Python backend.

**Non-Goals for this MVP:**

- Docker, PostgreSQL, Alembic migrations, or pgvector.
- OpenAI calls, embeddings, RAG, or generated scenarios and recommendations.
- Caregiver accounts, authentication, multiple caregiver roles, or production deployment.
- A full AAC board frontend, ARASAAC search integration, or individual response analytics.

## Decisions

### Use SQLite with the existing SQLAlchemy setup

Keep database setup local and direct. Use a SQLite database file and the project's existing SQLAlchemy model/session pattern. Create the MVP tables from SQLAlchemy metadata during application startup if needed. Do not add Alembic or Docker for this stage. Store flexible list/summary values using SQLAlchemy's generic `JSON` type, which works with SQLite; do not use PostgreSQL-only `JSONB`.

### Keep the data model focused on four tables

- **User**: a learner profile, including the selected age band, presentation settings, locations if currently required by the UI, and enabled communication goals. Store goals as a small validated list rather than adding goal catalog and join tables.
- **Symbol**: a preloaded, shared catalog entry with its word, word class, required image reference, and optional source/attribution fields.
- **UserSymbol**: the association between a learner and a catalog symbol. Avoid duplicating catalog metadata; this table represents each learner's collection membership and retains its learner-specific page/position as required by the vocabulary spec.
- **PracticeSession**: the learner, selected goal and format, scenario, completion status, timestamps, and a short final summary. Do not create response-event or analytics tables.

Use foreign keys from `UserSymbol` to both `User` and `Symbol`, and from `PracticeSession` to `User`. Deleting a user cascades to that user's `UserSymbol` associations and practice sessions, while preserving shared `Symbol` catalog entries. A catalog symbol may belong to multiple learner collections; deleting it from one collection removes only the association, not the shared catalog entry. Learner profiles can be created through the API without caregiver accounts or authentication. Keep the fictional learner fixture in `dummy_data.py` separate from SQLite; preload shared catalog symbols from that module's catalog fixture.

### Keep the first endpoint flow narrow

Expose only what is needed to demonstrate the backend flow:

- Create, list, read, update, and delete learner profiles.
- List the shared symbol catalog and add or remove catalog symbols from a learner's collection.
- Start a session for an enabled goal and a supported format, selecting a fixed scenario from the fixture data.
- Submit a response while the session is active.
- Complete the session and save a basic summary.

Keep trial events in runtime memory during the active session and persist only the completed summary. For a single-process demo, a restart may end an active session; explain this limitation rather than adding session infrastructure.

### Validate inputs with Pydantic and application checks

Use Pydantic schemas for request and response shapes and straightforward checks for enabled goals, supported formats, session status, and symbols belonging to the learner. Keep enumerations small and aligned across schemas and model behavior. Do not build a generic validation framework.

### Defer integrations until the flow works

Use a fictional learner fixture and fixed scenarios to validate endpoints. Preloaded symbol catalog entries are reference data persisted in SQLite; do not insert the fictional learner fixture automatically. Consider AI generation, guidance retrieval, ARASAAC import, recommendation review, and the browser board only after the SQLite endpoint flow is complete and the course scope still requires them.

## Risks / Trade-offs

- SQLite is suitable for local MVP work but does not address concurrent production use.
- Runtime session state disappears on restart. This is acceptable for testing the basic flow, but should be revisited if durable in-progress sessions become a requirement.
- The existing broader capability specs describe features beyond this MVP and must not be mistaken for work completed by this change's first slice.

## Implementation Sequence

1. Simplify database configuration to SQLite and make startup table creation work.
2. Agree the four model shapes and corresponding Pydantic schemas.
3. Add a fictional learner fixture, preload shared catalog symbols, and define fixed scenarios.
4. Implement and manually exercise profile and symbol endpoints.
5. Implement session start, response, and completion endpoints.
6. Demonstrate the entire flow using the API docs or simple HTTP requests, then decide which deferred capability is needed next.

## Open Questions

- Keep current profile settings only where they support the existing app flow; avoid adding new profile fields solely for hypothetical later features.
