# Spec Delta

## Purpose

Provides goal-focused AAC practice in which learners respond directly to accessible scenarios and caregivers receive evidence-grounded recommendations for review.

## ADDED Requirements

### Requirement: Practice is organized around communication goals
The system SHALL organize practice around caregiver-selected communication goals rather than a fixed PECS phase sequence.

#### Scenario: Start a goal-focused session
- **WHEN** a caregiver starts a session for an enabled goal
- **THEN** the system scopes practice to that goal and the learner's approved vocabulary

#### Scenario: Goals are not tied to a prescribed sequence
- **WHEN** a caregiver selects any enabled goal
- **THEN** the system allows practice of that goal without requiring completion of another goal or phase

### Requirement: Scenarios are accessible and vocabulary-bounded
The system SHALL present each generated scenario read aloud and SHALL display it using the learner profile's text-only or symbols-and-text setting.

#### Scenario: Generate a scenario for choice practice
- **WHEN** a choice-format session requests a scenario
- **THEN** the scenario uses the selected communication goal and approved vocabulary and provides a small set of response symbols

#### Scenario: Generate a scenario for sentence practice
- **WHEN** a sentence-format session requests a scenario
- **THEN** the scenario allows a multi-symbol response using the learner's approved vocabulary

#### Scenario: Do not reveal the intended response in the prompt
- **WHEN** a scenario is presented
- **THEN** its presentation does not highlight or otherwise disclose the intended response symbol or sequence

#### Scenario: Scenario output cannot be validated
- **WHEN** generated output fails schema validation or references unavailable vocabulary
- **THEN** the system does not present it and returns a recoverable error or requests a replacement

### Requirement: Learners respond directly in the app
The system SHALL let the learner respond to a scenario using the practice format selected for that session.

#### Scenario: Submit a symbol choice
- **WHEN** the learner selects a symbol in choice format
- **THEN** the system records the selection in runtime session state for summary calculation

#### Scenario: Submit a multi-symbol message
- **WHEN** the learner builds a message in sentence format
- **THEN** the system records the ordered symbol sequence in runtime session state for summary calculation

### Requirement: Practice uses a browser-based communication board
The system SHALL present learner practice in a computer-browser board with distinct prompt and response areas and a stable vocabulary order.

#### Scenario: Present a scenario prompt
- **WHEN** a practice turn begins
- **THEN** the prompt area presents the scenario as a situation or a direct question and provides a way to hear it again

#### Scenario: Present the response area
- **WHEN** the learner is responding
- **THEN** the response area shows selected symbols separately from the prompt and the vocabulary remains in its established order

### Requirement: Symbol board supports adjustable card size and scrolling
The system SHALL let the caregiver choose a card size that changes board density while preserving vocabulary order and allowing access to all symbols.

#### Scenario: Change card size
- **WHEN** a caregiver selects small, medium, or large cards
- **THEN** the board reflows to show more or fewer symbols while preserving their order

#### Scenario: Find symbols beyond the visible section
- **WHEN** a vocabulary section contains more symbols than fit on screen
- **THEN** the learner can scroll that section independently to reach the remaining symbols

### Requirement: Symbol selection speaks and builds a response
The system SHALL speak each selected symbol and let the learner edit the composed response before submitting it.

#### Scenario: Select a symbol
- **WHEN** the learner taps a vocabulary symbol
- **THEN** the symbol is added to the response in selection order and its word is spoken aloud

#### Scenario: Remove or clear response symbols
- **WHEN** the learner removes a selected response symbol or clears the response
- **THEN** the response area reflects that edit without changing the vocabulary board

#### Scenario: Speak and submit a response
- **WHEN** the learner activates Speak with a composed response
- **THEN** the system speaks the complete response and submits it for the current practice turn

#### Scenario: Acknowledge a submitted response
- **WHEN** a response has been submitted
- **THEN** the system shows a brief acknowledgment while the response remains visible, then clears it when the next prompt appears

### Requirement: Trial details are transient and summaries are retained
The system SHALL calculate session measures from runtime trial events and persist a session summary without persisting individual trial events.

#### Scenario: Complete a session
- **WHEN** the learner completes or ends a session
- **THEN** the system calculates and stores an evidence-rich summary and discards its individual runtime trial events

#### Scenario: Summary supports recommendation review
- **WHEN** a caregiver reviews a recommendation
- **THEN** the associated summary exposes the goal, format, scenario context, vocabulary involved, prompt counts, response outcomes, and applicable aggregate accuracy, independence, or response-time measures

### Requirement: Measurements are computed by the application
The system SHALL calculate reported counts and rates from runtime session events rather than asking the language model to calculate them.

#### Scenario: Calculate session measures
- **WHEN** a session ends
- **THEN** the system derives its stored counts and rates from the runtime event data using documented formulas

### Requirement: Recommendations are evidence-grounded and reviewable
The system SHALL present AI recommendations for vocabulary or future practice as pending caregiver decisions, with rationale linked to saved session evidence and retrieved guidance.

#### Scenario: Recommend next practice
- **WHEN** a completed session contains sufficient evidence for a next-practice suggestion
- **THEN** the system presents a recommendation with its goal or format, rationale, supporting summary evidence, and guidance sources

#### Scenario: Recommend vocabulary
- **WHEN** session evidence and retrieved guidance support a vocabulary suggestion
- **THEN** the system presents the suggested word and symbol as pending caregiver review with a rationale and evidence references

#### Scenario: Evidence is insufficient
- **WHEN** the available summaries or retrieved guidance do not support a recommendation
- **THEN** the AI response explicitly reports insufficient evidence and the system does not present a speculative recommendation as a conclusion

#### Scenario: Caregiver reviews a recommendation
- **WHEN** a caregiver approves or rejects a pending recommendation
- **THEN** the system records the decision and review time, and applies an approved vocabulary suggestion only after approval

### Requirement: AI recommendations never change learner settings autonomously
The system SHALL NOT change the learner's profile, active goals, practice format, or approved vocabulary without caregiver action.

#### Scenario: AI suggests a profile adjustment
- **WHEN** the AI recommends changing a goal or practice format
- **THEN** the system leaves the profile unchanged until the caregiver explicitly applies the suggestion
