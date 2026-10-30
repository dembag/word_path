# Tasks

## Ownership

- The learner writes the Python changes. The assistant explains one manageable next step, reviews the learner's code, and helps debug before moving to the next task.
- Verify behavior through the FastAPI docs or simple HTTP requests as each endpoint is completed. Do not expose internal expected responses through learner-facing API schemas.

## 1. AI service and question contracts

- [x] 1.1 Add typed internal and learner-facing question/session schemas, including optional location and a five-question response; verify schema validation accepts valid choice and sentence batches and rejects malformed output.
- [x] 1.2 Add OpenAI configuration loading and a small generation service using the existing package; verify missing credentials and provider errors become handled application errors without exposing secrets.
- [x] 1.3 Implement structured batch generation with one bounded correction attempt and vocabulary/context validation; verify every returned symbol belongs to the learner's approved vocabulary and expected responses are omitted from public questions.
- [x] 1.4 Document required OpenAI environment variables and local session-generation behavior; verify setup instructions match `.env.example`.

## 2. AI-backed session start

- [ ] 2.1 Resolve and validate learner, goal, format, vocabulary, and optional location before generation; verify a chosen saved location is honored, an omitted location is selected from saved locations, and an empty location list adds no location constraint.
- [ ] 2.2 Replace fixture-based production session creation with validated AI batch generation and persist only after all five questions pass validation; verify a failed generation creates no session and does not fall back to `SCENARIOS`.
- [ ] 2.3 Update the session response to return learner-facing questions and resolved context while keeping stored expected responses private; verify the API response contains exactly five questions and no answer key.
- [ ] 2.4 Confirm existing SQLite session rows remain intact and new sessions can be read after an app restart; verify no table drop or database recreation is used.

## 3. Runtime response events and measures

- [ ] 3.1 Define and implement response submission for a question in an active session, including response order and any support level needed for scoring; verify unknown questions and inactive sessions return errors without recording events.
- [ ] 3.2 Calculate and persist objective measures from runtime events when a session completes; document the formulas and verify the saved counts and rates match a manually worked sample session.
- [ ] 3.3 Clear transient response events after completion; verify completed session measures remain available while raw trial events do not.

## 4. Caregiver narrative and end-to-end flow

- [ ] 4.1 Generate a caregiver-friendly narrative from stored context and app-calculated measures, and store it separately from metrics; verify the AI is not asked to calculate counts or rates.
- [ ] 4.2 Preserve completed status and measures when narrative generation fails, and expose narrative unavailability in the API response; verify this path through a controlled provider failure.
- [ ] 4.3 Walk through session start, all five responses, completion, and summary retrieval using the API docs or simple HTTP requests; verify successful generation, validation failure, and narrative failure paths.
