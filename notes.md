
# Word Path
## Scope
- I am a student studying AI Software Engineering at Masterschool.
- This project is the main project for the course that demonstrates what I have learnt.

- Make me do most of the coding manually when you think it would benefit my learning.
- When you do any coding, explain step by step what you have done and why.
- Do the explanations as if I am a 5-year-old.
- If you are not sure about something, search the web or ask me.

## Aim
Create an AI enhanced learning/practice feature for a tablet based AAC (Augmented Alternative Communication) application.

## Design: AI-assisted AAC practice, in stages
### Core principles
- The layout never changes. Symbol and navigation positions stay fixed so motor memory builds. Only the difficulty around them changes: prompts, distractors, scenario complexity. 
- Core words first, fringe words second. Core words (want, more, stop, help, go) are reusable across every situation. Fringe words (apple, bubbles, Grandma) are personal and motivating, so they come from the caregiver. 
- Each phase has three steps: Guided, Partial, Independent. This is the prompt-fading ladder, and it makes progress measurable inside a phase, not only between phases. 
- The AI proposes and the caregiver decides. New vocabulary and phase changes both go through caregiver approval.

### Phase 0: Device orientation
- Goal: the learner understands that touching a symbol makes something happen, and finds the device rewarding. 
- Activities: cause-and-effect play. Touching a symbol speaks the word and shows a short reward (sound, animation, or the real item). The target symbol is highlighted. 
- Vocabulary: 2–4 highly preferred items, plus MORE. These are fringe words chosen by the caregiver. 
- Measured: touch accuracy, how quickly the learner first touches a target, and engagement (session length, voluntary touches).

### Phase I: Making requests
- Goal: spontaneous single-symbol requests. This is PECS Phase I. 
- Activities: scenarios where the learner wants something (“Snack time, and your favourite is on the table”). Guided → Partial → Independent. 
- Vocabulary: 4–8 symbols. Core: want, more, help, stop, all done. Fringe: 3–4 favourite items or activities. 
- Measured: independent requests per session, prompt level, response time.

### Phase II: Persistence and navigation
- Goal: keep communicating when the first attempt fails, and find symbols across pages. This is PECS Phase II (“distance and persistence”) adapted to a device. 
- Activities: scenarios with a barrier (“The cup is out of reach” → ask again or use help). Page navigation is introduced here, with MORE and BACK fixed in place. 
- Vocabulary: 10–15 symbols. Core: add go, look, yes, no, again. Fringe: a second page of items, people, and places. 
- Measured: persistence (retries after failure), navigation accuracy, wrong-page errors.

### Phase III: Discrimination
- Goal: choose the right symbol among several. This is PECS Phase III. 
- Activities: a growing field of 2 → 4 → 8 → the full page. Distractors are first very different, then visually and semantically similar (Juice and Apple). Difficulty rises through the distractor set, not through moving symbols. 
- Vocabulary: 20–40 symbols, with categories (food, activities, people, places) and the core words like, don’t want, different. 
- Measured: accuracy by field size, confusion pairs (which symbols get mixed up), latency.

### Phase IV: Sentence structure
- Goal: combine symbols into simple sentences. This is PECS Phase IV. 
- Activities: carrier phrases (“I want + [item]”), then adding modifiers and verbs (“I want + big + ball”). 
- Vocabulary: 40–80 symbols. Core: I, want, need, can, put, open, play, eat. Fringe: attribute words (colour, size) and more nouns. 
- Measured: sentence completion rate, word order, mean length of utterance, how often the learner builds a sentence with no prompt.

### Phase V: Answering questions
- Goal: respond to questions. This is PECS Phase V. 
- Activities: the AI poses questions in scenarios (“What do you want?”, “Who is this?”, “Where is the ball?”). 
- Vocabulary: 80–150 symbols. Core: what, who, where, yes, no, not, mine, his/hers. Fringe: personal vocabulary and familiar places. 
- Measured: correct answer rate by question type, latency from question to response, how often the learner answers without prompts.

### Phase VI: Commenting and social communication
- Goal: communicate for non-request reasons (sharing, commenting, social connection). This is PECS Phase VI plus social language. 
- Activities: open scenarios (“You see a dog…”), narrating, expressing feelings, greetings and goodbyes, and a limited amount of free expression. 
- Vocabulary: 150+ symbols. Core: I see, I hear, I feel, I think, hi, bye, please, thank you, plus feelings and social phrases. Fringe: wide, personalised, and growing. 
- Measured: non-request communications per session, spontaneous vs prompted use, vocabulary diversity (distinct symbols used), generalisation across scenarios.

### Making it measurable

Per trial, record:

- Prompt level: independent, partial, or full 
- Accuracy and response latency 
- Error type: wrong symbol, wrong page, no response, or tapping off-target 
- Target symbol, scenario, and context

Example mastery criteria (starting defaults, to be adjusted by the therapist per learner):

|   Metric  |   Threshold to be considered for the next phase   |
|-----------|---------------------------------------------------|
|   Independent responses |	≥80% across 3 consecutive sessions  |
|   Accuracy|	≥85%    |
|   Response time   |	Stable or improving over the last 5 sessions    |
|   Generalisation  |	Success with ≥3 different scenarios and ≥2 different vocabulary sets    |
|   Retention   |	Still meets criteria after a break (e.g. 1 week)    |

Regression rule: if performance drops below roughly 60% for 3 sessions, the AI recommends going back a step (a phase, or a step within the phase) and explains why.

### How the AI fits in
- Generates scenarios within the learner’s current vocabulary and phase. 
- Assesses each session: independence trend, error patterns, confusion pairs, engagement. 
- Suggests vocabulary (approved in profile settings). 
- Recommends phase changes with a rationale and the supporting numbers, e.g. “Independence 86% over the last 3 sessions, accuracy 89%, success in 4 scenarios. Recommend moving to Phase III. Caveat: the Juice/Apple confusion is still at 30%.” 
- Never moves symbols or advances the phase on its own.

### The caregiver dashboard (averages)
- Independence rate trend (per session and per week)
- Accuracy and response time by phase 
- Prompt-level distribution (how much support is still needed)
- Vocabulary mastery list: new, practising, or mastered 
- Confusion pairs and the most common error types 
- Pending suggestions (new vocabulary and phase recommendations) for approval

### Things to watch
- Thresholds depend on the learner. Someone with motor difficulties or very short sessions needs lower targets or a different measure, so make the criteria editable. 
- Averages can hide plateaus, so include a trend line, not just a mean. 
- Phases are not strictly sequential. Some learners need Phase III discrimination skills before Phase II persistence, so allow the caregiver to override the order.

## Database Schema
// Revised schema: session-level aggregates instead of trial-level logging.
// The app computes the numbers at session end; the AI writes the narrative and the recommendation.

Table users {
  user_id integer [pk, increment]
  name varchar(50) [not null, unique]
  learning_phase smallint [default: 0, note: 'Current phase 0-6. Source of truth; changes only on caregiver approval']
  learning_step varchar(20) [default: 'guided', note: 'guided | partial | independent']
  ai_can_add_vocab bool [default: false]
  card_size varchar(10) [note: 's | m | l']
  created_at timestamp
}

Table symbols {
  symbol_id integer [pk, increment]
  word varchar(50) [not null]
  source varchar(50)
  source_id varchar(100)
  label varchar(50)
  keywords text
  image_url text [not null]
  license varchar(60) [not null]
  license_url text
  author varchar(100)
  author_url text
  semantic_category varchar(50)
  raw_tags text
  card_local_path text
  fetched_at timestamp
}

Table vocabulary {
  vocabulary_id integer [pk, increment]
  user_id integer [not null, ref: > users.user_id]
  name varchar(100)
}

Table vocab_symbol {
  vocabulary_id integer [pk, ref: > vocabulary.vocabulary_id]
  symbol_id integer [pk, ref: > symbols.symbol_id]
  grid_page smallint [default: 1]
  grid_position smallint [note: 'Null while a suggestion is pending; assigned to an empty slot on approval']
  word_class varchar(10) [note: 'core | fringe']
  origin varchar(20) [note: 'caregiver | ai_suggested']
  status varchar(20) [default: 'active', note: 'active | pending | approved | rejected']
  added timestamp
  suggested_at timestamp
  reviewed_at timestamp
  symbol_rationale text [note: 'AI reason; null for caregiver-added words']

  indexes {
    (vocabulary_id, grid_page, grid_position) [unique]
  }
}

// One row per practice session
Table progression {
  progression_id integer [pk, increment]
  user_id integer [not null, ref: > users.user_id]
  session_start datetime
  session_end datetime
  learning_phase smallint
  learning_step varchar(20)

  // Computed by code, not by the AI
  trials_total integer
  accuracy float
  independence_rate float
  retry_rate float
  vocab_mastered_count integer
  prompt_counts jsonb [note: '{"independent":n,"visual_cue":n,"partial_assist":n,"full_assist":n}']
  symbol_results jsonb [note: '{"<symbol_id>": {"attempts":n,"independent":n,"errors":{"<chosen_symbol_id>":n}}}. Gives confusion pairs and per-word mastery without trial rows']
  context_tags jsonb [note: 'Scenario contexts used, e.g. ["home","shop"]. For generalisation']

  ai_assessment jsonb [note: 'Structured AI observations: trends, error patterns, engagement']
}

Table reports {
  id integer [pk, increment]
  user_id integer [not null, ref: > users.user_id]
  progression_id integer [not null, ref: > progression.progression_id]
  content text [note: 'AI-written narrative summary for the caregiver, including Phase recommendation']

  recommendation varchar(20) [default: 'none', note: 'none | advance | regress | hold']
  recommended_phase smallint
  phase_rationale text
  recommendation_status varchar(20) [note: 'pending | approved | rejected']
  recommended_at timestamp
  reviewed_at timestamp
  created_at timestamp
}

// Optional: cheap cross-session word mastery without trial rows
Table user_symbol_stats {
  user_id integer [pk, ref: > users.user_id]
  symbol_id integer [pk, ref: > symbols.symbol_id]
  attempts integer [default: 0]
  independent_count integer [default: 0]
  status varchar(20) [default: 'new', note: 'new | practising | mastered']
  last_practised_at timestamp
}

