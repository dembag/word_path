# Design

## Context

See proposal.md for motivation and specs/aac-practice-ui/spec.md for the learner-visible behavior. The project is a FastAPI app with Jinja2 installed and two starter templates (`layout.html` and `home.html`). The existing backend change is building JSON endpoints for profiles, vocabulary, and practice sessions. The UI should use those endpoints and remain approachable for a course MVP.

## Goals / Non-Goals

**Goals:**

- Give the learner a direct browser path through a practice session.
- Keep the implementation small enough for the learner to understand and maintain.
- Agree on the visual design and interaction flow with the user before writing interface code.

**Non-Goals:**

- Add a frontend framework or build pipeline before the design discussion establishes a need.
- Build caregiver analytics, recommendation review, AI generation, or ARASAAC search in this change.

## Decisions

### Make design discussion the first implementation checkpoint

After the backend API flow is complete, discuss the learner journey, page layout, visual direction, accessibility needs, speech controls, and technical approach with the user. Confirm the design and update this change's design, specs, and tasks before implementing the interface. The user requested this checkpoint so design choices can be made with them when the work reaches the UI stage.

### Start from the existing FastAPI and Jinja setup

The project already has Jinja2 and starter templates, with no frontend package manifest or build pipeline. The initial recommendation is to build on those templates and add only the browser-side behavior needed for interactive practice. Compare that approach with a client-rendered frontend at the design checkpoint; do not add a framework or dependency without agreement.

### Keep the UI connected to the backend session flow

The interface should start sessions, load the active prompt and learner vocabulary, submit responses, and complete sessions through the backend APIs. It should not write directly to the database or persist individual response events outside the session flow.

## Risks / Trade-offs

- **Backend API details may change while the current change is implemented** → Confirm routes and request/response shapes after the backend walkthrough, then align the UI tasks before coding.
- **Server-rendered templates may need browser-side code for interactive responses and speech** → Keep that code focused on the practice board and confirm the balance at the design checkpoint.
- **AAC use varies by learner** → Review prompt mode, card size, vocabulary order, and keyboard/accessibility needs with the user before implementation.

## Migration Plan

No data migration is expected. Add interface routes and assets alongside the API, and retain the JSON API for direct use and documentation.

## Open Questions

- At the design checkpoint, agree on the learner journey, visual direction, and whether the existing Jinja setup is sufficient for the interaction model.
