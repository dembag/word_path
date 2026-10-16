# Design

## Context

This is a course MVP for a small FastAPI app. The mentor's guidance is to focus on backend endpoints and demonstrate the flow with dummy data, using SQLite and avoiding infrastructure work that does not help the first demonstration.

## Goals / Non-Goals

**Goals:**

- Provide a simple API flow for one learner to practise a communication goal.
- Persist the learner profile, learner vocabulary, and completed session summary in SQLite.
- Use fixed dummy scenarios so the flow works without network access or model credentials.
- Keep the implementation approachable and explainable as the learner writes most of the Python backend.

**Non-Goals for this MVP:**

- Docker, PostgreSQL, Alembic migrations, or pgvector.
- OpenAI calls, embeddings, RAG, or generated scenarios and recommendations.
- Accounts, authentication, multiple caregiver roles, or production deployment.
- A full AAC board frontend, ARASAAC search integration, or individual response analytics.

## Decisions

### Use SQLite with the existing SQLAlchemy setup

Keep database setup local and direct. Use a SQLite database file and the project's existing SQLAlchemy model/session pattern. Create the MVP tables from SQLAlchemy metadata during application startup if needed. Do not add Alembic or Docker for this stage. Store flexible list/summary values using SQLAlchemy's generic `JSON` type, which works with SQLite; do not use PostgreSQL-only `JSONB`.

### Keep the data model to three tables

- **User**: the learner profile, including the selected age band, presentation settings, locations if currently required by the UI, and enabled communication goals. Store goals as a small validated list for this single-user MVP rather than adding goal catalog and join tables.
- **UserSymbol**: a word or phrase available to the learner, with its image reference and optional source/attribution fields. Keep it user-owned; do not introduce a separate global symbol catalog.
- **PracticeSession**: the learner, selected goal and format, scenario, completion status, timestamps, and a short final summary. Do not create response-event or analytics tables.

Use simple foreign keys from `UserSymbol` and `PracticeSession` to `User`. Scenario fixtures live in a small Python module, not another database table. Use a single clearly documented demo learner if account identity is not yet part of the existing app flow.

### Keep the first endpoint flow narrow

Expose only what is needed to demonstrate the backend flow:

- Read and update the learner profile.
- List and add learner symbols.
- Start a session for an enabled goal and a supported format, selecting a fixed scenario from the fixture data.
- Submit a response while the session is active.
- Complete the session and save a basic summary.

Keep trial events in runtime memory during the active session and persist only the completed summary. For a single-process demo, a restart may end an active session; explain this limitation rather than adding session infrastructure.

### Validate inputs with Pydantic and application checks

Use Pydantic schemas for request and response shapes and straightforward checks for enabled goals, supported formats, session status, and symbols belonging to the learner. Keep enumerations small and aligned across schemas and model behavior. Do not build a generic validation framework.

### Defer integrations until the flow works

Use fictional seeded data and fixed scenarios to validate endpoints. Consider AI generation, guidance retrieval, ARASAAC import, recommendation review, and the browser board only after the SQLite endpoint flow is complete and the course scope still requires them.

## Risks / Trade-offs

- SQLite and a single-user demo are suitable for local MVP work but do not address concurrent production use.
- Runtime session state disappears on restart. This is acceptable for testing the basic flow, but should be revisited if durable in-progress sessions become a requirement.
- The existing broader capability specs describe features beyond this MVP and must not be mistaken for work completed by this change's first slice.

## Implementation Sequence

1. Simplify database configuration to SQLite and make startup table creation work.
2. Agree the three model shapes and corresponding Pydantic schemas.
3. Add small fictional fixtures for one learner, symbols, and scenarios.
4. Implement and manually exercise profile and symbol endpoints.
5. Implement session start, response, and completion endpoints.
6. Demonstrate the entire flow using the API docs or simple HTTP requests, then decide which deferred capability is needed next.

## Open Questions

None block the basic endpoint slice. Keep current profile settings only where they support the existing app flow; avoid adding new profile fields solely for hypothetical later features.
