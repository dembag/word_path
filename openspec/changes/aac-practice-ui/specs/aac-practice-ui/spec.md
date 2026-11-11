# Spec Delta

## Purpose

Gives learners a browser-based AAC practice interface for reading or hearing a scenario and composing a response with their approved vocabulary. The interface presents practice in a clear, accessible flow while preserving caregiver-selected settings and vocabulary order.

## ADDED Requirements

### Requirement: Learner can select an existing profile
The interface SHALL provide a splash page listing existing learner profiles and SHALL open a pre-session screen for the selected profile.

#### Scenario: Profiles are available
- **WHEN** a learner opens the interface
- **THEN** the splash page lists the available profiles by name

#### Scenario: Learner selects a profile
- **WHEN** a learner selects a profile
- **THEN** the interface opens that learner's pre-session screen and uses that profile for subsequent practice

### Requirement: Learner can manage their full profile before practice
The interface SHALL provide access to full profile settings from the pre-session screen and SHALL keep profile settings unavailable during an active practice session.

#### Scenario: Open profile settings before practice
- **WHEN** a learner chooses Settings from the pre-session screen
- **THEN** the interface displays and allows editing of the learner's name, age band, prompt display, starting format, communication goals, locations, and card size

#### Scenario: Save profile settings
- **WHEN** the learner saves valid profile changes
- **THEN** the interface updates the selected learner profile and returns to the pre-session screen

#### Scenario: Settings during an active session
- **WHEN** a practice session is active
- **THEN** the interface does not provide a way to open profile settings

### Requirement: Learner can start an enabled practice session
The interface SHALL let a learner begin a session from the pre-session screen using a goal enabled on their profile and the profile's configured starting format.

#### Scenario: Choose an enabled goal
- **WHEN** a learner starts practice
- **THEN** the interface offers only communication goals enabled for that learner

#### Scenario: Use the configured practice format
- **WHEN** a learner starts practice
- **THEN** the interface uses the format configured on the learner's profile

#### Scenario: Goal is not enabled
- **WHEN** a requested goal is not enabled for the learner
- **THEN** the interface reports that practice cannot start with that goal

### Requirement: Practice prompt follows learner display settings
The interface SHALL present the current scenario according to the learner's prompt display setting and provide a way to hear it read aloud again.

#### Scenario: Text-only prompt
- **WHEN** the learner profile uses text-only prompts
- **THEN** the prompt area presents the scenario text without response symbols

#### Scenario: Symbols-and-text prompt
- **WHEN** the learner profile uses symbols-and-text prompts
- **THEN** the prompt area presents the scenario text with its supporting symbols when available

#### Scenario: Replay a prompt
- **WHEN** the learner asks to hear the prompt again
- **THEN** the interface reads the current prompt aloud

### Requirement: Practice board separates prompt and response
The interface SHALL show the scenario prompt, composed response, and learner vocabulary in distinct areas while preserving the vocabulary's assigned order and the prototype's color-separated sections.

#### Scenario: Present a practice turn
- **WHEN** a scenario is ready for a response
- **THEN** the learner can distinguish the prompt area from the response area and vocabulary board

#### Scenario: Preserve vocabulary order
- **WHEN** the vocabulary board is displayed
- **THEN** symbols appear in their assigned page and position order

#### Scenario: Show unavailable choice symbols
- **WHEN** the session format is choice
- **THEN** all profile vocabulary remains visible in its assigned order, while symbols outside the current question's available choices appear dimmed and cannot be selected

#### Scenario: Use the full vocabulary for sentence responses
- **WHEN** the session format is sentence
- **THEN** all profile vocabulary symbols remain selectable in their assigned order

### Requirement: Learner can compose and edit a response
The interface SHALL support a single-symbol choice response and an ordered multi-symbol sentence response according to the session format.

#### Scenario: Select a symbol
- **WHEN** the learner selects a vocabulary symbol
- **THEN** the symbol is added to the response in selection order and its word is spoken aloud

#### Scenario: Edit the response
- **WHEN** the learner removes a selected symbol from the response
- **THEN** the response area updates without changing the vocabulary board

#### Scenario: Speak and submit a response
- **WHEN** the learner submits a composed response
- **THEN** the interface speaks the composed words and submits the response for the current turn

### Requirement: Choice questions provide timed cues and answer feedback
For choice sessions, the interface SHALL start the cue schedule when a question first appears, provide immediate visual and sound feedback for each submitted answer, and allow the learner to retry.

#### Scenario: Verbal cue time is reached
- **WHEN** 10 seconds have elapsed since the current question first appeared and it remains on screen
- **THEN** the interface speaks the correct answer

#### Scenario: Visual cue time is reached
- **WHEN** 20 seconds have elapsed since the current question first appeared and it remains on screen
- **THEN** the interface visually highlights the correct answer

#### Scenario: Correct choice is submitted
- **WHEN** the learner submits the correct choice
- **THEN** the selected symbol's border flashes green and the interface plays a happy ding

#### Scenario: Incorrect choice is submitted
- **WHEN** the learner submits an incorrect choice
- **THEN** the selected symbol's border flashes red, the interface plays the normal selection click, and the learner may retry or continue

#### Scenario: Learner retries a choice question
- **WHEN** the learner submits another answer for the same question
- **THEN** the cue schedule continues from the question's original display time without restarting

#### Scenario: Learner leaves a choice question
- **WHEN** the learner advances to another question or finishes the session
- **THEN** any remaining cues for the previous question stop

#### Scenario: Score a choice question with retries
- **WHEN** the session results are calculated
- **THEN** accuracy and independence use the first submitted answer for that question, and later submissions do not change those scores

### Requirement: Learner can navigate choice questions at any time
The interface SHALL keep the **Next** action available from the moment a choice question appears, including when the learner has not answered or has submitted an incorrect answer. The final question SHALL provide **Finish** from the moment it appears. Navigation controls SHALL show a matching application control symbol and text label, independently of the learner's selectable vocabulary.

#### Scenario: Continue without submitting an answer
- **WHEN** the learner selects **Next** without submitting an answer
- **THEN** the interface advances and the question is recorded as unanswered

#### Scenario: Continue after an incorrect answer
- **WHEN** the learner selects **Next** after an incorrect submission
- **THEN** the interface advances while the first submitted answer remains the scored answer

#### Scenario: Finish the final question
- **WHEN** the learner selects **Finish** on the final question
- **THEN** the interface completes the session and displays the session summary, including unanswered questions

#### Scenario: Show navigation controls
- **WHEN** **Next** or **Finish** is displayed
- **THEN** the control shows its matching symbol alongside its text label

#### Scenario: Highlight forward navigation after a submitted answer
- **WHEN** a response is saved for the current question
- **THEN** **Next** is highlighted light green, or **Finish** is highlighted light green when the current question is the final one

### Requirement: Learner can adjust vocabulary board density
The interface SHALL honor the learner's selected card size and keep every vocabulary symbol visible or reachable by scrolling without changing its assigned order. Selection availability SHALL follow the active practice format and question.

#### Scenario: Change card size
- **WHEN** the learner or caregiver selects small, medium, or large cards
- **THEN** the board changes its visible density while keeping the symbol order

#### Scenario: Reach symbols outside the visible area
- **WHEN** vocabulary extends beyond the visible board area
- **THEN** the learner can scroll to see the remaining symbols, while only symbols available for the current question can be selected

### Requirement: Vocabulary board uses three landscape sections
The learner interface SHALL use a landscape layout with Personal on the left, Core beside it, and General filling the remaining board area on the right. The section names SHALL remain available to assistive technology while their headings stay visually hidden. Personal SHALL use one tile column over a light blue background; Core SHALL use three tile columns over a faded purple background; General SHALL use the remaining width over a faded beige background. Words assigned to any page other than `personal` or `core` SHALL appear in General. Personal tiles SHALL use medium size when the profile selects small or medium cards and large size when the profile selects large cards.

#### Scenario: Present the three vocabulary sections
- **WHEN** a practice board contains Personal, Core, and General vocabulary
- **THEN** Personal appears at the left in one column, Core appears beside it in three columns, and General fills the remaining area on the right

#### Scenario: Use the Personal tile size override
- **WHEN** the profile selects small or medium cards
- **THEN** Personal tiles use medium size while Core and General follow the selected card size

#### Scenario: Show General vocabulary
- **WHEN** a vocabulary item is assigned to a page other than `personal` or `core`
- **THEN** the practice board places it in General

#### Scenario: Request landscape orientation
- **WHEN** Word Path is opened in portrait orientation
- **THEN** the interface hides its normal page content and asks the user to rotate the device to landscape

### Requirement: Practice interface fills the browser viewport
The practice interface SHALL fill the browser viewport without an enclosing tablet-style frame in landscape orientation. The prompt and response strips SHALL size their symbols to match the small main-board tiles and have enough height to show each complete tile. The question strip SHALL size to its contents with 10px padding around question symbols. Vocabulary tiles SHALL retain their 4:5 shape.

#### Scenario: Present a practice turn
- **WHEN** a practice question is active
- **THEN** the prompt appears above the response strip and the vocabulary board remains below them

#### Scenario: Use the full browser viewport
- **WHEN** the practice interface is displayed at different browser viewport sizes or device emulations
- **THEN** the interface fills the viewport without an outer tablet frame, the prompt, response, and board strips keep the same relative heights, and vocabulary tiles keep their 4:5 shape

#### Scenario: Fit question symbols in the prompt strip
- **WHEN** the prompt includes supporting symbols
- **THEN** the symbol tiles match the small main-board tile size, preserve their complete images with 10px padding around them, and remain horizontally reachable when they exceed the strip width; the Listen symbol control appears at their right at the same height

#### Scenario: Fit response symbols in the response strip
- **WHEN** the learner composes a response
- **THEN** response tiles match the small main-board tile size, preserve their complete images, and the response strip is tall enough to contain them

### Requirement: Interface acknowledges submitted responses
The interface SHALL acknowledge a submitted response and keep it visible until the next prompt is presented.

#### Scenario: Response submitted
- **WHEN** the learner submits a response
- **THEN** the interface shows the applicable answer feedback and keeps the response visible until the next prompt

#### Scenario: Next prompt appears
- **WHEN** the next practice prompt is presented
- **THEN** the previous response is cleared from the response area
