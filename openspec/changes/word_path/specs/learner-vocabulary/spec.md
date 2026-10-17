# Spec Delta

## Purpose

Defines learner profile settings and approved symbol vocabulary used to tailor AAC practice while preserving caregiver control over profile changes and vocabulary approval.

## ADDED Requirements

### Requirement: Shared symbols are stored in a preloaded catalog
The system SHALL store reusable symbols in a shared catalog and associate catalog entries with learners through the learner vocabulary.

#### Scenario: Preload catalog symbols
- **WHEN** the application initializes the local catalog
- **THEN** it makes the predefined symbols available for learners to add to their collections

#### Scenario: Add catalog symbol to learner collection
- **WHEN** a caregiver adds an available catalog symbol to a learner's vocabulary
- **THEN** the system creates a learner-to-symbol association without duplicating the catalog entry

### Requirement: Caregiver can configure the learner profile
The system SHALL allow a caregiver to adjust practice settings through the learner's profile without requiring a caregiver account.

#### Scenario: Create learner profile
- **WHEN** a caregiver submits a new learner profile with valid settings
- **THEN** the system stores the profile and returns its identifier and profile data

#### Scenario: List learner profiles
- **WHEN** a caregiver requests the learner profiles
- **THEN** the system returns the stored profiles

#### Scenario: Read learner profile
- **WHEN** a caregiver requests a stored learner profile by identifier
- **THEN** the system returns that profile or reports that it does not exist

#### Scenario: Delete learner profile
- **WHEN** a caregiver deletes a stored learner profile
- **THEN** the system removes that profile and its learner-symbol associations and practice sessions, while preserving shared catalog symbols

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

#### Scenario: Delete learner symbol
- **WHEN** a caregiver deletes a symbol from a learner's vocabulary
- **THEN** the system removes that learner-to-symbol association without deleting the shared catalog entry or affecting other learners' collections

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
