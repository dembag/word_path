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
- **WHEN** the learner removes a selected symbol or clears the response
- **THEN** the response area updates without changing the vocabulary board

#### Scenario: Speak and submit a response
- **WHEN** the learner submits a composed response
- **THEN** the interface speaks the composed words and submits the response for the current turn

### Requirement: Learner can adjust vocabulary board density
The interface SHALL honor the learner's selected card size and keep every vocabulary symbol visible or reachable by scrolling without changing its assigned order. Selection availability SHALL follow the active practice format and question.

#### Scenario: Change card size
- **WHEN** the learner or caregiver selects small, medium, or large cards
- **THEN** the board changes its visible density while keeping the symbol order

#### Scenario: Reach symbols outside the visible area
- **WHEN** vocabulary extends beyond the visible board area
- **THEN** the learner can scroll to see the remaining symbols, while only symbols available for the current question can be selected

### Requirement: Practice interface follows the landscape tablet layout
The interface SHALL use the prototype's landscape tablet layout as its primary practice presentation, keeping the prompt, response strip, and color-separated vocabulary board spatially distinct.

#### Scenario: Present a practice turn
- **WHEN** a practice question is active
- **THEN** the prompt appears above the response strip and the vocabulary board remains below them

### Requirement: Interface acknowledges submitted responses
The interface SHALL acknowledge a submitted response and keep it visible until the next prompt is presented.

#### Scenario: Response submitted
- **WHEN** the learner submits a response
- **THEN** the interface shows a brief acknowledgment and keeps the response visible until the next prompt

#### Scenario: Next prompt appears
- **WHEN** the next practice prompt is presented
- **THEN** the previous response is cleared from the response area
