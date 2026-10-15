# Spec Delta

## Purpose

Defines learner profile settings and approved symbol vocabulary used to tailor AAC practice while preserving caregiver control over profile changes and vocabulary approval.

## ADDED Requirements

### Requirement: Caregiver can configure the learner profile
The system SHALL allow a caregiver to adjust practice settings through the learner's profile without requiring a caregiver account.

#### Scenario: Update profile settings
- **WHEN** a caregiver edits and saves the learner profile
- **THEN** the system stores the selected age band, optional locations, prompt display mode, communication goals, and starting practice format for that learner

#### Scenario: Validate profile settings
- **WHEN** a profile update contains an unsupported age band, prompt mode, or practice format
- **THEN** the system rejects the invalid value and preserves the last valid setting

### Requirement: Age band guides themes without determining ability
The system SHALL use the caregiver-selected age band only to guide age-appropriate scenario themes and SHALL NOT infer a learner's cognitive or communication ability from age.

#### Scenario: Generate age-aware scenario
- **WHEN** a scenario is generated for a learner with an age band
- **THEN** its themes are suitable for that band while its communication complexity follows the selected goal, vocabulary, and practice format

### Requirement: Approved vocabulary is associated with the learner
The system SHALL maintain an approved vocabulary for each learner and preserve assigned symbol positions when suggestions are reviewed.

#### Scenario: Add approved symbol
- **WHEN** a caregiver adds an available symbol to the learner vocabulary
- **THEN** the system associates it with the learner and records its word class and assigned page and position

#### Scenario: Preserve symbol position
- **WHEN** vocabulary is suggested or approved
- **THEN** existing approved symbols do not move unless the caregiver explicitly edits their positions

### Requirement: ARASAAC symbols retain attribution and license metadata
The system SHALL retain source identifiers and required attribution and license information for ARASAAC symbols it displays or stores.

#### Scenario: Import an ARASAAC symbol
- **WHEN** a symbol is imported from ARASAAC
- **THEN** its source ID, image reference, author, source, license, and attribution are stored when provided or required by ARASAAC terms

#### Scenario: Display symbol attribution
- **WHEN** an ARASAAC symbol is displayed in the application
- **THEN** the required attribution and license information is available in the interface or an accessible attribution view

### Requirement: AI vocabulary suggestions remain pending until caregiver approval
The system SHALL keep AI-suggested vocabulary separate from the learner's approved vocabulary until a caregiver approves it.

#### Scenario: Review vocabulary suggestion
- **WHEN** a caregiver approves a pending vocabulary suggestion
- **THEN** the system adds the symbol to the approved learner vocabulary and assigns an available position without moving existing symbols

#### Scenario: Reject vocabulary suggestion
- **WHEN** a caregiver rejects a pending vocabulary suggestion
- **THEN** the system records the rejection and leaves the approved vocabulary unchanged
