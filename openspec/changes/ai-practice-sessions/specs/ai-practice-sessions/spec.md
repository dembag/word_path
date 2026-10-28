# Spec Delta

## Purpose

Provides AI-generated, vocabulary-bounded AAC practice sessions and reliable session records that combine application-calculated measures with caregiver-friendly narrative summaries.

## ADDED Requirements

### Requirement: Session context must be authorized by the learner profile
The system SHALL start practice only for a learner's enabled communication goal and supported practice format, using an optional location drawn from that learner's saved locations.

#### Scenario: Caregiver selects a saved location
- **WHEN** a session request includes a location saved in the learner profile
- **THEN** the system uses that location as context for every question in the session

#### Scenario: Requested location is not saved
- **WHEN** a session request includes a location that is not in the learner profile
- **THEN** the system rejects the request and does not create a session

#### Scenario: Requested goal or format is not enabled
- **WHEN** a session request uses a goal or format not enabled for that learner
- **THEN** the system rejects the request and does not create a session

### Requirement: Omitted session locations are resolved from learner preferences
The system SHALL use one consistent location for a session, selected from the learner's saved locations when the caregiver omits a location.

#### Scenario: Learner has saved locations
- **WHEN** a session request omits location and the learner has one or more saved locations
- **THEN** the system randomly selects one saved location and uses it for every question

#### Scenario: Learner has no saved locations
- **WHEN** a session request omits location and the learner has no saved locations
- **THEN** the system generates questions without a location constraint

### Requirement: Sessions contain five AI-generated questions
The system SHALL generate a complete batch of five questions at session start using the requested goal and format, the learner's approved vocabulary, and the resolved location when present.

#### Scenario: Generate a complete session
- **WHEN** a valid session request is processed
- **THEN** the system returns five questions aligned with the requested goal and format and restricted to the learner's approved vocabulary

#### Scenario: Use choice format
- **WHEN** the requested practice format is choice
- **THEN** each question provides a prompt, a small set of response symbols from approved vocabulary, and an internal expected response

#### Scenario: Use sentence format
- **WHEN** the requested practice format is sentence
- **THEN** each question supports an ordered multi-symbol response using approved vocabulary and has an internal expected response

#### Scenario: Keep expected responses hidden
- **WHEN** the session questions are returned for learner practice
- **THEN** expected responses are excluded from the learner-facing response

### Requirement: Generated questions must be validated before a session is created
The system SHALL validate the generated batch for its required structure, count, selected context, and vocabulary references before persisting or returning an active session.

#### Scenario: Generated batch is valid
- **WHEN** all five generated questions pass validation
- **THEN** the system creates and returns the active session with the validated questions

#### Scenario: Generation fails or output remains invalid
- **WHEN** the AI service fails or the generated batch remains invalid after the bounded retry
- **THEN** the system returns a recoverable error, creates no active session, and does not substitute fixed test scenarios

### Requirement: Active session responses are transient
The system SHALL retain question response events only for the lifetime of the active application process and use them to calculate session measures.

#### Scenario: Submit a response to an active question
- **WHEN** a learner submits a response to a question in an active session
- **THEN** the system records the response event in runtime state and acknowledges the submission

#### Scenario: Submit a response to an unavailable session or question
- **WHEN** a response refers to a missing, completed, or unknown question
- **THEN** the system returns an error and records no response event

### Requirement: The application calculates objective session measures
The system SHALL calculate counts and rates from recorded response events and SHALL NOT rely on AI-generated values for objective measurements.

#### Scenario: Complete a session
- **WHEN** the caregiver or learner completes a session
- **THEN** the system calculates objective measures from its response events, persists them with the completed session, and clears transient events

### Requirement: AI narrative summaries are grounded in calculated measures
The system SHALL use AI only to write a caregiver-friendly narrative from the completed session context and application-calculated measures.

#### Scenario: Narrative generation succeeds
- **WHEN** AI summary generation succeeds
- **THEN** the completed session stores the narrative alongside the objective measures

#### Scenario: Narrative generation fails
- **WHEN** AI summary generation fails
- **THEN** the system still completes the session and persists objective measures, and the API reports that the narrative is unavailable
