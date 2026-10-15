# Design

## Context

See `proposal.md` for motivation and scope. The current project is a small FastAPI/SQLAlchemy app backed by a hard-coded SQLite URL. User routes are mostly backed by an in-memory list or are placeholders. `data_models.py`, `api_schemas.py`, and `notes.md` disagree about fields and PECS phase ranges; `data_manager.py` also contains a malformed sessionmaker keyword. There is no visible dependency manifest or migration setup.

## Goals / Non-Goals

**Goals:**

- Deliver a demonstrable caregiver-configured profile, direct learner practice flow, and caregiver review flow.
- Demonstrate corpus preprocessing, semantic retrieval, OpenAI structured outputs, and grounded recommendation behavior.
- Use PostgreSQL as the application database and retain no individual trial rows after session completion.
- Keep the architecture small enough to explain and operate as a course project.

**Non-Goals:**

- Build caregiver accounts, authentication, or multi-tenant authorization.
- Diagnose a learner, prescribe therapy, or automatically change vocabulary, goals, or practice format.
- Reproduce a full AAC application or implement every activity and dashboard metric in `notes.md`.
- Use the model for arithmetic, infer ability from age, or generate speech audio.

## Decisions

### PostgreSQL is the application database

Use a `DATABASE_URL` environment setting and SQLAlchemy's PostgreSQL driver. Add schema migrations so the existing SQLite-era model can be replaced without relying on ad hoc table creation. Use PostgreSQL `JSONB` only for structured data whose shape can evolve, such as session summaries, scenario metadata, and recommendation evidence; keep frequently filtered values (learner, goal, format, status, timestamps) in typed columns.

The `users` table represents the learner profile, matching the current routes. It stores the age band, prompt display preference, starting practice format, and optional locations. There is no caregiver table or caregiver identity; caregiver changes are actions in the profile/review interface.

**Alternative considered:** Retain SQLite. It has lower setup cost and is adequate for a small single-process demo, but the user explicitly chose PostgreSQL and the earlier JSONB schema aligns with it.

### Use pgvector for curated guidance retrieval

Store source metadata and reviewed text chunks in PostgreSQL. Store each chunk's `text-embedding-3-small` vector in a pgvector column and perform cosine similarity retrieval in PostgreSQL. Record chunk IDs used for each generated scenario and recommendation. Start with exact nearest-neighbor search; the curated corpus is small, so approximate indexes are unnecessary.

**Alternative considered:** Compute cosine similarity over vectors in Python. That avoids a PostgreSQL extension but leaves vector retrieval outside the chosen database and makes the RAG path less visible. If pgvector cannot be installed in the target environment, retain the same chunk/embed API and use exact in-process cosine similarity as a documented fallback.

### Persist profile, approved vocabulary, sources, sessions, and recommendations

Use normalized relational tables for `users`, communication goals and their learner association, `symbols`, approved `user_symbols`, guidance sources/chunks, `practice_sessions`, the session-to-guidance-chunk association, and `recommendations`.

`practice_sessions` stores scenario metadata and the final computed summary. It does not have a trial table. A session holds its events in process memory until it ends; completion computes measurements, writes one session summary, and clears the events. A restart before completion loses the active session, which is acceptable for this demo and should be shown as a limitation.

Vocabulary suggestions are recommendation records until approved. Approval creates the learner-symbol association and assigns a free position; it never moves existing symbols. Remove phase fields, `progression`, duplicate `reports`, and cross-session `user_symbol_stats` from the proposed feature schema. Trends can initially be derived from stored session summaries.

### Separate deterministic calculations from model interpretation

Application code calculates counts and rates from temporary events using explicit formulas. The model receives profile settings needed for the task, approved vocabulary, these computed measures, and retrieved AAC excerpts. It returns a Pydantic-validated structured scenario or recommendation with rationale and evidence references. The application validates that referenced symbols belong to approved vocabulary and evidence IDs came from the current retrieval/session context before display.

Use `gpt-4o-mini` for scenario generation and summary analysis and `text-embedding-3-small` for chunk and query embeddings. Keep both model names configurable. Store API credentials only in environment variables; never place them in source, database rows, or logs. Avoid sending learner names or unnecessary identifying data to the model.

### Curate excerpts before indexing

Maintain source title, organization, URL, attribution, reuse terms, and reviewed excerpt text. Preprocessing normalizes encoding and whitespace and removes extraction artifacts; a human reviews resulting chunks before indexing. Start with English AAC guidance from credible sources, and include only excerpts whose reuse terms permit the intended project use. PECS material is optional and is not the organizing framework.

### Keep read-aloud separate from model generation

The model returns text and structured content. The tablet/browser's text-to-speech reads prompts aloud. The profile setting selects text-only or symbols-plus-text display. Scenario symbols and response options are resolved against approved vocabulary; presentation must not reveal the intended response.

### Serve the learner board as a browser frontend through FastAPI
Use the existing standalone HTML, CSS, and JavaScript prototype as the starting point for the learner board, and serve the finished frontend through the FastAPI application. The board targets a computer-browser demonstration. Keep its prompt and response strips separate from the stable, color-separated vocabulary sections, and scale the board to fit the browser viewport without changing the section order. The frontend handles display and learner interactions; FastAPI endpoints own session state, scenario generation, response submission, summary calculation, and recommendations.

**Alternative considered:** Keep the prototype as an independent static demo. That would preserve its simplicity, but would leave the learner interface disconnected from the FastAPI and AI features the project is demonstrating. A separate frontend framework is also unnecessary for this small interface and would add another stack to explain.

### Reflow card grids while preserving vocabulary order
The caregiver-selected small, medium, or large card size controls how many symbols fit in each board section. Reflow the grid when the size changes, but retain the vocabulary's established order. If a section contains more symbols than fit in its visible area, make that section independently vertically scrollable so the prompt, response, and other sections remain in place.

### Treat Speak as response submission
Tapping a vocabulary tile appends its word to the response and speaks that word immediately. The response area supports removing an individual selection and clearing the draft. Speak reads the complete composed response and submits it for the current turn. Show a brief acknowledgment with the submitted response still visible; clear the response when the next prompt is presented. Prompt text may be a short situational statement or a direct question, depending on the generated scenario, and can be replayed.

### Keep implementation ownership aligned with the learning goal
The coding assistant can implement the browser interface and its calls to the API. The learner will implement most Python backend work, including data models, routes, session handling, AI integration, and server-side validation. Keep frontend and backend tasks explicit enough that the API contract forms a clear handoff and the learner can build and understand the backend themselves.

## Risks / Trade-offs

- [Risk] PostgreSQL and pgvector add local setup and dependency work → Provide a reproducible local configuration and document the extension requirement; keep exact Python cosine as a fallback for environments where the extension cannot be installed.
- [Risk] In-memory events are lost on server restart and are unsafe across multiple worker processes → Run the demo with one app process and clearly scope active-session state to that process; persist only the final summary as requested.
- [Risk] A valid JSON response can still be inappropriate or unsupported → Use strict structured output, server-side schema and reference validation, evidence sufficiency rules, and caregiver review.
- [Risk] Session summaries can hide individual errors → Include the per-goal, per-symbol, prompt, and outcome aggregates needed to explain recommendations, while explicitly accepting that individual interactions cannot be audited later.
- [Risk] Source materials or ARASAAC assets may have reuse restrictions → Retain attribution and license data and review terms before bundling content or distributing the demo.
- [Risk] Age-based presentation could be mistaken for an ability judgment → Use only caregiver-selected age bands for themes; derive practice complexity from selected format, goal, and vocabulary.

## Migration Plan

1. Add PostgreSQL and pgvector local setup, environment-based connection configuration, and migration tooling.
2. Define PostgreSQL models and initial migration for learner profiles, vocabulary, corpus, sessions, and recommendations; remove obsolete phase/report/stat structures from the target schema.
3. Align Pydantic schemas and routes with the new models and update `notes.md` to reflect goal-based practice and summary-only persistence.
4. Seed reviewed guidance and sample learner/symbol data, then implement the RAG and practice flow.
5. Existing local SQLite data is dummy/demo data and is not migrated automatically. A fresh PostgreSQL database is initialized from migrations and seed data. Rollback for development is to stop the app and return to the prior SQLite checkout; no production-data rollback path is required.

## Open Questions

None that block the initial course-demo plan. Exact age-band labels, communication goal labels, and initial source excerpt selection can be finalized while implementing profile and corpus seed data without changing the capability boundaries.
