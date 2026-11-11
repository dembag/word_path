# Tasks

## Ownership

- The assistant implements the learner interface after the design checkpoint and backend API contracts are confirmed. The user steers the experience and reviews the browser behavior.
- Keep the implementation within FastAPI, Jinja, HTML, CSS, and focused JavaScript. Do not add a frontend framework or build pipeline without revisiting the design.

## 1. Design and API checkpoint

- [x] 1.1 Complete the backend API walkthrough for profile selection/settings and the full session flow (start, response submission, retries, and completion); confirm the request/response contracts for UI integration, including scoring from the first submitted answer and unanswered questions. The UI design decisions are recorded in the proposal, spec, and design artifacts.

## 2. Learner practice interface

- [x] 2.1 Build the profile splash and pre-session screen using existing learner profiles, enabled goals, and configured starting format; verify profile selection leads to the correct pre-session screen.
- [x] 2.2 Build full profile settings for name, age band, prompt display, starting format, communication goals, locations, and card size; save changes through the profile API and keep settings unavailable during active practice.
- [x] 2.3 Present each scenario in the top prompt panel, honor the learner's prompt display setting, and provide prompt replay; verify text-only and symbols-and-text modes.
- [ ] 2.4 Render profile vocabulary in assigned position order across Personal, Core, and General; map legacy People and other page values to those sections. Use one Personal column on the left, three Core columns beside it, and let General fill the remaining width. Apply light blue, faded purple, and faded beige section backgrounds; keep Personal cards medium for small or medium profile settings and large for large settings. Keep all vocabulary reachable, and in choice mode dim and disable symbols outside the current question's available choices. Keep the interface landscape-only, fill the browser viewport, match question and response tiles to the small main-board tile size, place **Hear again** to the right of question symbols at the same height, size the question strip to its tiles with 10px padding and avoid cropping, and preserve 4:5 tile shapes. Verify selection, board order, and responsive sizing in the browser.
- [x] 2.5 Implement choice and sentence response composition, automatic symbol speech, response editing, Speak, and Submit. In choice mode, add 10-second spoken and 20-second visual cues, immediate sound and border feedback, retries, and first-answer scoring; keep Next available from question display and show symbol-plus-label navigation controls.
- [x] 2.6 Connect session completion to the backend and present the resulting completion state; make Finish available from the final question's display and include unanswered questions in the summary.
- [x] 2.7 Ensure the attempt and completion flow records retries while calculating accuracy and independence from each question's first submitted answer; preserve questions with no submission as unanswered.

## 3. Integration and handoff

- [ ] 3.1 Walk through a complete learner session in the browser, including profile selection, settings, session start, prompt replay, choice cues, correct and incorrect feedback, retries, advancing with unanswered questions, and completion; record and resolve integration issues found.
- [ ] 3.2 Update local setup notes with how to launch and use the learner interface; verify the documented steps reach the UI in a browser.
