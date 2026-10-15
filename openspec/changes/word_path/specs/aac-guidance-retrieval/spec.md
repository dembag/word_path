# Spec Delta

## Purpose

Provides a small, reviewed English-language AAC guidance corpus that can be cleaned, searched, and cited when generating practice scenarios and recommendations.

## ADDED Requirements

### Requirement: Guidance excerpts have reviewable provenance
The system SHALL retain source and reuse information for every excerpt made available for retrieval.

#### Scenario: Add a guidance excerpt
- **WHEN** a reviewer adds an excerpt to the corpus
- **THEN** the system stores its text, source title, organization, URL, topic, attribution, and known reuse terms

#### Scenario: Excerpt reuse terms are unclear
- **WHEN** an excerpt's reuse permission is unknown or incompatible with the intended use
- **THEN** the excerpt is not included in a distributable corpus until its use is resolved

### Requirement: Guidance text is cleaned and prepared for retrieval
The system SHALL preprocess reviewed excerpts to normalize text and remove extraction artifacts while preserving the source meaning and provenance.

#### Scenario: Clean imported document text
- **WHEN** source material is prepared for indexing
- **THEN** the preprocessing pipeline normalizes whitespace and encoding, removes repeated headers or irrelevant page artifacts, and retains a link to the original source

#### Scenario: Review prepared excerpts
- **WHEN** preprocessing produces candidate chunks
- **THEN** a reviewer can inspect and approve the chunks before they are used for retrieval

### Requirement: Retrieve relevant guidance with source identity
The system SHALL retrieve relevant reviewed excerpts for the active communication goal and return source identifiers with each excerpt.

#### Scenario: Retrieve guidance for scenario generation
- **WHEN** a practice scenario is requested for a communication goal
- **THEN** retrieval returns a bounded set of relevant excerpts and their source metadata for the scenario-generation request

#### Scenario: No relevant excerpt is found
- **WHEN** retrieval finds no excerpt relevant enough to support a request
- **THEN** the system reports that guidance context is unavailable and does not fabricate a citation

### Requirement: Embeddings correspond to the configured model
The system SHALL associate each stored guidance embedding with its embedding model and source chunk, and SHALL use compatible query embeddings for retrieval.

#### Scenario: Embed a reviewed chunk
- **WHEN** a reviewed chunk is indexed
- **THEN** the system creates and stores its embedding using the configured `text-embedding-3-small` model

#### Scenario: Embedding model changes
- **WHEN** the configured embedding model changes
- **THEN** the system does not compare new query vectors against incompatible stored vectors and requires re-indexing or a compatible index
