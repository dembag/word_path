# Design

## Context

The current `POST /sessions` selects one object from `dummy_data.SCENARIOS` and stores it in `PracticeSession.scenario`. The existing request carries learner, communication goal, and practice format; learner profiles already store locations and vocabulary associations. OpenAI's Python package and example environment settings are present, but no API call is implemented. See proposal.md for motivation and the capability spec for behavior.

## Goals / Non-Goals

**Goals:**

- Keep session creation and completion in the existing FastAPI and SQLite application.
- Generate and validate five questions in one AI request before creating an active session.
- Keep internal expected responses separate from the learner-facing question response.
- Retain response events in process memory and persist calculated measures with a completed session.
- Make AI narrative generation a separate completion step whose failure does not discard measured results.

**Non-Goals:**

- Retrieval augmented generation, embeddings, recommendations, or autonomous learner-profile changes.
- Frontend work, durable event-by-event analytics, or surviving in-progress sessions after process restart.
- Replacing fixed fixture scenarios for manual testing; they are simply not a fallback for production session creation.

## Decisions

### Use the existing OpenAI configuration

Create a small service boundary for question generation and narrative generation, configured from `OPENAI_API_KEY` and `OPENAI_MODEL`. Load local environment values through the existing application setup without committing secrets. Keep prompts and response validation in the service layer so route logic remains understandable. If credentials are missing or the provider is unavailable, return the specified recoverable session-start error; do not silently switch to fixtures.

**Alternative considered:** Add a provider abstraction or another AI dependency. This adds complexity without a current second provider requirement.

### Resolve context before prompting

Validate learner, enabled goal and format, and an explicitly requested location against the profile before calling the model. When location is omitted, choose one saved learner location uniformly at random; use no location constraint for an empty list. Load only that learner's associated vocabulary and pass the chosen words and symbol identifiers as the generation boundary. Use the same location and vocabulary boundary for all five questions.

**Alternative considered:** Let the model choose a location or invent vocabulary. That would make learner settings unreliable and could produce unselectable responses.

### Generate one validated batch before persistence

Request a structured batch of exactly five questions, then validate its shape, goal, format, location context, choice/sentence rules, vocabulary references, and expected responses in application code. Allow one bounded correction attempt with validation feedback. Persist nothing until the entire batch is valid. The internal representation contains expected responses; the public response schema contains only the prompt and learner-selectable content.

**Alternative considered:** Generate questions one at a time. Batch generation matches the agreed upfront flow and gives the session a coherent context.

### Store questions as session content and preserve existing data

Change the model and response contract from a single `scenario` to a `questions` list, with a distinct internal expected-response representation. Keep the question content and internal answer data in the existing JSON-backed session storage for the SQLite MVP, but define separate Pydantic shapes so answer keys cannot leak. Existing historical rows with a single scenario will remain readable as legacy records; newly started sessions use the questions contract. Avoid dropping or recreating the local database.

**Alternative considered:** Add Alembic migration infrastructure now. The project intentionally deferred migration tooling for the local MVP; the JSON column can hold the new representation without a database schema change.

### Keep response events transient and measurements deterministic

Use a process-local mapping keyed by session ID for response events, including question identifier, response, submission time, and any explicitly recorded support/prompt level needed for independence measures. Validate session status and question membership before adding events. On completion, calculate the agreed counts, accuracy, independence, and response-time measures in Python; document the formulas and represent unavailable measures as unavailable instead of guessing. Save those measures before requesting narrative text, then clear response events.

**Alternative considered:** Ask the model to score responses or store every trial. Model scoring is not reproducible, while event persistence is outside the lightweight MVP and the agreed transient-event design.

### Treat narrative text as optional enrichment

Generate the narrative from the stored session context and already-computed measures. Store it separately from the measurements in the summary JSON. If narrative generation fails, preserve completion and measures and mark the narrative unavailable in the API response.

**Alternative considered:** Roll back session completion on an AI summary failure. That would discard reliable evidence because a nonessential prose step failed.

## Risks / Trade-offs

- [Provider latency or outage prevents a new session] → Bound the request and correction attempt, return a recoverable error, and do not create a partial session.
- [Generated content can still be inappropriate despite structural validation] → Restrict prompts to the learner context and approved vocabulary, validate every symbol reference, and keep this MVP's caregiver review/front-end flow in scope for later work.
- [Process restart clears in-progress response events] → Document this local MVP limitation; only completed metrics are durable.
- [Legacy session rows contain a single scenario] → Keep legacy data intact and make new response handling distinguish legacy rows from new question batches.
- [SQLite JSON representations vary in shape] → Validate stored question and summary data through explicit Pydantic models at API boundaries.

## Migration Plan

1. Add typed generation, public question, response-event, and summary contracts while keeping the SQLite database file intact.
2. Update session creation to validate context, generate and validate the full question batch, then persist the session.
3. Add transient response submission and deterministic completion calculations; persist computed measures before narrative generation.
4. Preserve access to existing scenario rows, and return the new questions field for newly created sessions.
5. If implementation reveals that JSON storage cannot safely distinguish legacy rows, stop and propose a non-destructive migration before changing the database.

Rollback consists of reverting application code while retaining the existing JSON column and database file; do not drop tables or delete saved session data.

## Open Questions

None. The MVP uses a fixed batch size of five and one bounded validation correction attempt; both can be revisited after observing generation quality.
