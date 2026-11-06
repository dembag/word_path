# Tasks

## Ownership

- The assistant implements the learner interface after the design checkpoint and backend API contracts are confirmed. The user steers the experience and reviews the browser behavior.
- Keep the implementation within FastAPI, Jinja, HTML, CSS, and focused JavaScript. Do not add a frontend framework or build pipeline without revisiting the design.

## 1. Design and API checkpoint

- [ ] 1.1 Complete the backend API walkthrough for profile selection/settings and the full session flow (start, response submission, and completion); confirm the request/response contracts for UI integration. The UI design decisions are recorded in the proposal, spec, and design artifacts.

## 2. Learner practice interface

- [ ] 2.1 Build the profile splash and pre-session screen using existing learner profiles, enabled goals, and configured starting format; verify profile selection leads to the correct pre-session screen.
- [ ] 2.2 Build full profile settings for name, age band, prompt display, starting format, communication goals, locations, and card size; save changes through the profile API and keep settings unavailable during active practice.
- [ ] 2.3 Present each scenario in the top prompt panel, honor the learner's prompt display setting, and provide prompt replay; verify text-only and symbols-and-text modes.
- [ ] 2.4 Render all profile vocabulary in assigned page and position order, honor card size, and allow board scrolling; in choice mode, dim and disable symbols outside the current question's available choices. Verify selection and board order in the browser.
- [ ] 2.5 Implement choice and sentence response composition, automatic symbol speech, response editing, Speak, Clear, Submit, and acknowledgment behavior; verify selection order and submitted responses.
- [ ] 2.6 Connect session completion to the backend and present the resulting completion state; verify the browser session is saved by the session API.

## 3. Integration and handoff

- [ ] 3.1 Walk through a complete learner session in the browser, including profile selection, settings, session start, prompt replay, response submission, and completion; record and resolve integration issues found.
- [ ] 3.2 Update local setup notes with how to launch and use the learner interface; verify the documented steps reach the UI in a browser.
