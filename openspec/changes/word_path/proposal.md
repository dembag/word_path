# Proposal

## Why

The project aims to help AAC users practise communicating with a tablet, but the current app contains only a basic in-memory user list and placeholder feature routes. A focused end-to-end practice flow will demonstrate the course's NLP, preprocessing, RAG, structured model output, API integration, prompt engineering, and GenAI ethics goals while replacing the notes' PECS-phase framing with broader communication goals.

## What Changes

- Add caregiver-editable learner profiles without caregiver accounts, including age band, optional locations, prompt presentation, active communication goals, and starting practice format.
- Add approved learner vocabulary sourced from ARASAAC, retaining symbol source, attribution, and license metadata; AI vocabulary suggestions require caregiver review.
- Add direct learner practice organized around requesting, sharing information, social interaction, and communication repair. Support small-choice symbol selection and multi-symbol sentence building.
- Curate and preprocess English AAC guidance excerpts for retrieval. Generate structured scenarios and evidence-grounded recommendations with OpenAI `gpt-4o-mini`; use `text-embedding-3-small` for retrieval.
- Keep trial details in memory during a session. Persist an evidence-rich session summary, guidance provenance, and caregiver-reviewed recommendations rather than every interaction.
- Replace PECS phase progression and phase-based measures in the feature design with goal- and format-based practice. Configure PostgreSQL for persistence and assess pgvector for corpus retrieval.
- Keep the OpenAI API key in an environment variable; never store or commit it.

## Capabilities

### New Capabilities

- `aac-practice`: Direct AAC practice sessions, scenario generation, session summaries, and evidence-based recommendations for caregiver review.
- `learner-vocabulary`: Learner profile settings, approved vocabulary, ARASAAC symbol metadata, and vocabulary suggestion review.
- `aac-guidance-retrieval`: Curated, cleaned AAC guidance excerpts and retrieval with source provenance for scenario and recommendation generation.

### Modified Capabilities

None. The project currently has no OpenSpec capability specs.

## Impact

- Existing FastAPI routes, SQLAlchemy models/database configuration, Pydantic schemas, templates, and `notes.md` require alignment; many routes are placeholders and current schemas disagree about profile fields and phase ranges.
- Replace the SQLite connection with PostgreSQL configuration and add migrations/schema creation appropriate to the project. Use PostgreSQL JSONB for structured records; use pgvector only if its setup is proportionate to the curated corpus and course demo.
- Add OpenAI client integration for embeddings and structured scenario/recommendation output. TTS is a client/device presentation concern and does not require model-generated audio.
- Add ARASAAC API integration and preserve required attribution/license information. Curated guidance excerpts must retain source and reuse terms.
- Keep session trial events transient; do not persist raw per-interaction records.
