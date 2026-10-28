# Proposal

## Why

The fixed scenario fixture only proves that a practice session can start; it does not support Word Path's intended AI-assisted practice. The app needs to create a short, learner-specific set of AAC questions and preserve reliable session evidence for a caregiver summary.

## What Changes

- Generate five practice questions together when a session starts, using the requested communication goal and format, the learner's approved vocabulary, and an optional session location.
- Let the caregiver choose a saved learner location; if none is requested, choose randomly from saved locations, and omit the location constraint when the learner has none.
- Return the generated questions as the session content and stop using fixed scenarios as the active session source.
- Keep per-question response events transient, calculate objective measures in the application, and ask AI to write a caregiver-friendly narrative from those measures and the session context.
- Return a recoverable error and do not create an active session when question generation fails validation or cannot be completed. Preserve the completed session and computed measures if narrative generation fails, and report that the narrative is unavailable.

## Capabilities

### New Capabilities
- `ai-practice-sessions`: Generate and validate multi-question AAC practice sessions and produce evidence-grounded caregiver narratives.

### Modified Capabilities

None. The repository has no main specs yet; this change establishes a new capability.

## Impact

- Changes the `POST /sessions` request and response contract to support an optional location and a batch of questions.
- Affects `main.py`, `api_schemas.py`, `data_models.py`, session runtime state, and configuration documentation.
- Uses the existing OpenAI package and environment configuration. It does not add retrieval, recommendation generation, frontend work, or a new database service.
