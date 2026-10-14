# Tasks

## Ownership

- The coding assistant implements the browser interface in HTML, CSS, and JavaScript, starting from `prototype/`, and connects it to the agreed FastAPI endpoints.
- The learner implements most Python backend work: database models and migrations, FastAPI routes, session state, AI integration, validation, and summary calculations.
- Agree on request and response shapes at the API boundary before wiring each browser flow to it; the learner should be able to explain and maintain the backend implementation.

## 1. PostgreSQL foundation

- [ ] 1.1 Add a dependency manifest and environment configuration for PostgreSQL, SQLAlchemy, migrations, pgvector, and the OpenAI SDK; verify a clean environment can install the declared dependencies without exposing secrets.
- [ ] 1.2 Add a reproducible local PostgreSQL/pgvector setup and document how to start and stop it; verify the database accepts a connection using `DATABASE_URL`.
- [ ] 1.3 Replace the hard-coded SQLite engine with environment-based PostgreSQL configuration and correct the SQLAlchemy session factory; verify the FastAPI app starts and opens a database session.
- [ ] 1.4 Add an initial migration for learners, goals, symbols, approved vocabulary, guidance sources/chunks, practice sessions, session guidance links, and recommendations; verify a fresh database upgrades to the expected schema.

## 2. Learner profiles and vocabulary

- [ ] 2.1 Align SQLAlchemy models and Pydantic schemas around the learner profile settings, with no caregiver account model; verify profile values are validated consistently on create and update.
- [ ] 2.2 [Backend: learner; frontend: coding assistant] Implement profile read/update routes and a caregiver-editable profile view for age band, optional locations, prompt display mode, communication goals, and starting format; verify edits persist after reload through the browser.
- [ ] 2.3 Implement ARASAAC symbol search/import and persist source IDs, image references, author, attribution, and license metadata; verify imported symbol details remain available to the UI.
- [ ] 2.4 Implement approved learner vocabulary and pending vocabulary suggestions, preserving existing grid positions; verify only caregiver approval adds a suggested symbol to the learner vocabulary.

## 3. Curated AAC guidance and retrieval

- [ ] 3.1 Select a small set of English AAC guidance sources and excerpt content whose reuse terms permit the course demo; record source URLs, attribution, topic, and reuse terms and verify each indexed excerpt has that provenance.
- [ ] 3.2 Implement text preprocessing and reviewed chunk storage; verify representative source text has normalized encoding/whitespace, extraction artifacts removed, and source links preserved.
- [ ] 3.3 Generate and store `text-embedding-3-small` vectors for approved chunks and implement pgvector similarity retrieval (with the documented exact-cosine fallback); verify a sample goal query returns relevant chunks and their source IDs.

## 4. Direct learner practice

- [ ] 4.1 Implement session creation using an enabled communication goal, learner settings, and approved vocabulary; verify a session cannot reference a disabled goal or unapproved symbol.
- [ ] 4.2 Define strict structured-output schemas and prompts for `gpt-4o-mini` scenarios, including goal, age band themes, context, allowed vocabulary, format, and acceptable responses; verify invalid or out-of-vocabulary output is rejected before display.
- [ ] 4.3 [Frontend: coding assistant] Adapt `prototype/` into the learner practice board served through FastAPI, with separate prompt and response areas, replayable situational or question prompts, immediate speech on symbol selection, editable response symbols, Speak-to-speak-and-submit, brief acknowledgment, response clearing on the next prompt, small/medium/large card reflow, and independent section scrolling; verify the full interaction and profile-selected prompt display modes in a computer browser.
- [ ] 4.4 Keep trial events in runtime session state and implement documented application-side summary calculations; verify session completion persists one evidence-rich summary and leaves no individual trial rows.

## 5. Evidence-grounded analysis and caregiver review

- [ ] 5.1 Implement structured session analysis using the saved summary and retrieved guidance, with explicit evidence references and an insufficient-evidence outcome; verify referenced session and guidance IDs belong to the request context.
- [ ] 5.2 Implement recommendation persistence and review actions for vocabulary and next-practice suggestions; verify pending suggestions do not change profile or vocabulary until caregiver approval.
- [ ] 5.3 [Frontend: coding assistant; API: learner] Add a caregiver summary/recommendation view showing computed measures, rationale, and guidance provenance; verify the browser displays each recommendation with links to its supporting summary and excerpts.

## 6. Integration and course demonstration

- [ ] 6.1 Update `notes.md` and project setup documentation to replace PECS phase progression with communication goals and document PostgreSQL, environment variables, RAG preprocessing, structured outputs, and ARASAAC attribution; verify documented setup steps match the implementation.
- [ ] 6.2 Walk through one complete demo using a seeded learner, approved symbols, one communication goal, a generated scenario, learner response, stored summary, and caregiver-reviewed recommendation; verify the flow works end to end with PostgreSQL and the configured OpenAI models.
- [ ] 6.3 Review the repository and generated artifacts to confirm API keys, learner names, and unnecessary identifying details are absent from source control, database seed data, and model requests.
