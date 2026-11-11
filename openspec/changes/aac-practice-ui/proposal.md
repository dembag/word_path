# Proposal

## Why

The project currently focuses on a backend API, while learners need a browser interface to take part in AAC practice directly. The interface will use the existing tablet-board prototype as its visual starting point and connect learner profiles to the practice session flow.

## What Changes

- Add a profile splash page that lists existing learner profiles and opens a pre-session screen for the selected learner.
- Add full profile settings on the pre-session screen, with no access to settings while a practice session is active.
- Add a browser-based AAC practice interface for viewing a scenario and composing a reply with the learner's vocabulary.
- Add choice-mode timed cues, immediate sound and visual correctness feedback, retry support, and question navigation that remains available from the start of each question.
- Preserve the prototype's landscape tablet layout, color-separated vocabulary sections, and message strip, adding a prompt area and session controls.
- Connect profile, vocabulary, and session interactions to the existing FastAPI endpoints using Jinja templates and focused JavaScript.

## Capabilities

### New Capabilities
- `aac-practice-ui`: Learner-facing browser interface for selecting a profile and completing accessible AAC practice sessions.

### Modified Capabilities

None.

## Impact

- Adds FastAPI page routes, Jinja templates, and browser-side JavaScript and styles alongside the existing JSON API.
- Uses the existing learner profile, vocabulary, and practice-session endpoints.
- Does not add profile creation, caregiver analytics, recommendation review, AI integration, a frontend framework, or a build pipeline.
