# Proposal

## Why

The project currently focuses on a backend API, while learners need a browser interface to take part in AAC practice directly. A separate UI change will turn the completed session flow into a usable learner experience, with design decisions discussed before interface coding begins.

## What Changes

- Add a browser-based learner interface for choosing an enabled practice goal and format, viewing a scenario, and responding with the learner's vocabulary.
- Provide distinct prompt, response, and vocabulary areas, with speech and response editing behavior described by the practice requirements.
- Make the visual design, page flow, and implementation approach an explicit discussion checkpoint before UI implementation tasks begin.
- Connect the interface to the existing learner, vocabulary, and practice-session API as those backend endpoints become available.

## Capabilities

### New Capabilities
- `aac-practice-ui`: Learner-facing browser interface for starting and completing accessible AAC practice sessions.

### Modified Capabilities

## Impact

- FastAPI routes and Jinja templates, with any supporting static assets or browser-side behavior agreed at the design checkpoint.
- Existing learner, vocabulary, and practice-session API endpoints.
- No caregiver account system or AI integration is included in this UI change.
