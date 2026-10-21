# Spec Delta

## Purpose

Gives learners a browser-based AAC practice interface for reading or hearing a scenario and composing a response with their approved vocabulary. The interface presents practice in a clear, accessible flow while preserving caregiver-selected settings and vocabulary order.

## ADDED Requirements

### Requirement: Learner can start an enabled practice session
The interface SHALL let a learner begin a session using a goal enabled on their profile and a supported practice format.

#### Scenario: Choose an enabled goal and format
- **WHEN** a learner starts practice
- **THEN** the interface offers only goals enabled for that learner and supported formats

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
The interface SHALL show the scenario prompt, composed response, and available learner vocabulary in distinct areas while preserving the vocabulary's assigned order.

#### Scenario: Present a practice turn
- **WHEN** a scenario is ready for a response
- **THEN** the learner can distinguish the prompt area from the response area and vocabulary board

#### Scenario: Preserve vocabulary order
- **WHEN** the vocabulary board is displayed
- **THEN** symbols appear in their assigned page and position order

### Requirement: Learner can compose and edit a response
The interface SHALL support a single-symbol choice response and an ordered multi-symbol sentence response according to the session format.

#### Scenario: Select a symbol
- **WHEN** the learner selects a vocabulary symbol
- **THEN** the symbol is added to the response in selection order and its word is spoken aloud

#### Scenario: Edit the response
- **WHEN** the learner removes a selected symbol or clears the response
- **THEN** the response area updates without changing the vocabulary board

#### Scenario: Speak and submit a response
- **WHEN** the learner submits a composed response
- **THEN** the interface speaks the composed words and submits the response for the current turn

### Requirement: Learner can adjust vocabulary board density
The interface SHALL honor the learner's selected card size and allow access to every vocabulary symbol without changing its assigned order.

#### Scenario: Change card size
- **WHEN** the learner or caregiver selects small, medium, or large cards
- **THEN** the board changes its visible density while keeping the symbol order

#### Scenario: Reach symbols outside the visible area
- **WHEN** vocabulary extends beyond the visible board area
- **THEN** the learner can scroll to and select the remaining symbols

### Requirement: Interface acknowledges submitted responses
The interface SHALL acknowledge a submitted response and keep it visible until the next prompt is presented.

#### Scenario: Response submitted
- **WHEN** the learner submits a response
- **THEN** the interface shows a brief acknowledgment and keeps the response visible until the next prompt

#### Scenario: Next prompt appears
- **WHEN** the next practice prompt is presented
- **THEN** the previous response is cleared from the response area
