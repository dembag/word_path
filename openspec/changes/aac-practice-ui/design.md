# Design

## Context

The project is a FastAPI application with Jinja2 installed, starter templates in `templates/`, and JSON endpoints for learner profiles, vocabulary, and practice sessions. The `prototype/` directory contains a landscape tablet-style AAC board with a top message strip, Speak and Clear actions, and three fixed color-separated vocabulary sections. This change adapts that visual language to the practice session API and adds profile selection and settings.

## Goals / Non-Goals

**Goals:**

- Give learners a direct browser path from profile selection through a complete practice session.
- Preserve the prototype's landscape tablet layout, color-separated board sections, message strip, and stable vocabulary positions.
- Provide a profile splash page and full profile settings before a session starts.
- Keep the implementation understandable and within the existing FastAPI, Jinja, HTML, CSS, and JavaScript stack.
- Connect profile, vocabulary, and session interactions to existing API endpoints.

**Non-Goals:**

- Creating or deleting learner profiles in the interface.
- Opening profile settings during an active practice session.
- Adding a frontend framework, build pipeline, caregiver analytics, recommendations, or AI integration.
- Replacing the prototype's AAC board visual language.

## Decisions

### Use a profile splash and a pre-session screen

The splash page lists existing profiles. Selecting a profile opens a pre-session screen with the learner's profile summary, enabled communication goals, configured starting format, a Start Practice action, and a Settings action. Settings opens the selected learner's full profile editor. Saving settings returns to the pre-session screen. Once a session starts, the active practice view has no Settings action; the profile cannot be changed mid-session.

Profile selection and editing use the existing `/users`, `/users/{user_id}`, and `PATCH /users/{user_id}` APIs. The settings editor covers the profile fields already supported by `UserUpdate`: name, age band, prompt display, starting format, communication goals, locations, and card size. Profile creation and deletion remain outside this interface.

### Fill the browser viewport with the practice board

Fill the browser viewport with the practice interface and remove the enclosing tablet-style frame. Keep the prompt and response strip tiles the same size as the small board tiles (84 by 105 CSS pixels), and size the question strip to its contents with 10px padding around the question tiles. Place the Listen symbol control to the right of the question symbols at the same height as the tiles. Keep the main vocabulary tiles at a 4:5 aspect ratio while their displayed size adapts to the board. Preserve the prototype's color-separated sections and assigned tile positions.

### Place prompt, response, and vocabulary in separate areas

During practice, show the current scenario in a prompt panel at the top, with prompt replay. Follow it with the prototype's persistent message strip, extended with Speak, Clear, and Submit controls. Keep the color-separated vocabulary board below. Honor the learner's text-only or symbols-and-text prompt setting.

When a symbol is selected, add it to the message strip in selection order and speak its word. Speak plays the composed message; Clear removes the current composition; Submit speaks the composed response and submits it to the active session. In choice mode, flash the selected symbol's border green and play a happy ding for a correct answer; flash it red and play the normal selection click for an incorrect answer. Keep the response visible until the learner moves on, and allow retries.

### Keep all vocabulary visible while constraining choice selections

Render the complete profile vocabulary in assigned page and position order. For a choice question, use `available_symbol_ids` to keep current choices at full emphasis and selectable; show other symbols dimmed and non-selectable. Keep the dimmed symbols and labels legible and convey their unavailable state to assistive technology. For sentence practice, all profile vocabulary remains selectable. Honor the profile's card size without changing symbol order.

### Time choice cues and scoring from the first response

Start the choice cue schedule when a question first appears. At 10 seconds, speak the correct answer; at 20 seconds, visually highlight it. Keep the schedule running from that original display time during retries, and stop pending cues when the learner leaves the question. Keep **Next** available from the start of each question and **Finish** available from the start of the final question. Each control shows its matching application control symbol and text label, independently of the learner's selectable vocabulary. Highlight the applicable forward action after a response is saved. A question advanced past without a submitted answer is unanswered. Use the first submitted answer for accuracy and independence; retries provide practice and feedback without changing those scores. Show unanswered questions in the completed session summary.

### Use Jinja with focused JavaScript

Build the browser interface using the existing FastAPI and Jinja setup, with focused JavaScript for profile selection, settings updates, session state, vocabulary selection, speech, and API calls. This avoids a separate frontend build pipeline while keeping the interactive behavior in browser code. Keep template routes and JSON endpoints on the same FastAPI application.

### Confirm backend contracts before UI integration

The UI depends on the session start, response submission, and completion contracts. Confirm their request and response shapes through the backend API walkthrough before implementing the integration. The profile and vocabulary APIs are already available.

## Risks / Trade-offs

- **The board has less vertical space after adding a prompt panel and response controls** -> Scale the landscape board while keeping touch targets usable; allow board scrolling for vocabulary beyond the visible area.
- **Dimmed symbols may be mistaken for unavailable content or become hard to read** -> Preserve label legibility, provide a non-color cue and accessible unavailable state, and block activation for unavailable choice symbols.
- **Profile fields may not fit comfortably on one screen** -> Use a dedicated pre-session settings view that returns to the selected learner's pre-session screen.
- **Speech support varies by browser and operating system** -> Keep the visual composition visible and retain manual Speak control even when automatic speech is unavailable.
- **The completion API is still being walked through** -> Confirm its behavior before connecting the UI completion flow.

## Migration Plan

No data migration is expected. Add page routes, Jinja templates, and static assets alongside the JSON API. Keep the API available for direct use and documentation.

## Open Questions

- Sentence response appropriateness assessment remains undecided pending comparison of candidate LLMs. The choice-session flow can be implemented independently of that decision.
- The browser walkthrough will identify integration details that depend on the completed session API contract.
