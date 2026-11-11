"""
Seed vocabulary for the initial symbol library.

Organized by semantic category so each fetched symbol can be auto-tagged
without manual review. Categories map to a rough default PECS phase — the
earliest phase a word is typically introduced — which you can override
per-user later based on the caregiver's actual teaching plan.

This list intentionally starts small (~100 words across 8 categories).
Add more words per category as your practice-scenario categories grow
(Week 7 of the implementation plan: mealtime, school, greetings, emotions).
"""

# category -> (default_pecs_phase, [words])
CORE_VOCAB = {
    "food_drink": (1, [
        "apple", "banana", "bread", "cheese", "cookie", "cracker", "egg",
        "grapes", "juice", "milk", "pizza", "sandwich", "water", "yogurt",
        "cereal", "pasta", "chicken", "soup", "ice cream", "chips",
    ]),
    "action_request": (1, [
        "eat", "drink", "want", "more", "finished", "help", "open", "close",
        "go", "stop", "play", "give", "look", "listen", "wash", "sit",
        "stand", "wait", "again", "turn",
    ]),
    "emotion": (2, [
        "happy", "sad", "angry", "scared", "tired", "hurt", "sick", "excited",
        "surprised", "bored", "calm", "frustrated",
    ]),
    "greeting_social": (2, [
        "hello", "goodbye", "please", "thank you", "yes", "no", "sorry",
        "excuse me", "my turn", "your turn",
    ]),
    "person": (3, [
        "mom", "dad", "teacher", "friend", "sister", "brother", "doctor",
        "baby", "grandma", "grandpa",
    ]),
    "place": (3, [
        "home", "school", "bathroom", "outside", "park", "kitchen",
        "bedroom", "playground", "car", "store",
    ]),
    "toy_activity": (1, [
        "ball", "book", "music", "tablet", "swing", "bubbles", "puzzle",
        "blocks", "crayon", "game",
    ]),
    "descriptor": (4, [
        "big", "small", "hot", "cold", "fast", "slow", "loud", "quiet",
        "clean", "dirty",
    ]),
}


def iter_seed_words():
    """Yield (word, category, default_phase) tuples for ingestion."""
    for category, (phase, words) in CORE_VOCAB.items():
        for word in words:
            yield word, category, phase


if __name__ == "__main__":
    words = list(iter_seed_words())
    print(f"Total seed words: {len(words)}")
    for category, (phase, words_in_cat) in CORE_VOCAB.items():
        print(f"  {category:<18} phase>={phase}  ({len(words_in_cat)} words)")
