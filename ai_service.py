import os
from functools import lru_cache
import json
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from api_schemas import (
    GeneratedQuestion,
    GeneratedQuestionBatch,
    GeneratedReview,
    SESSION_QUESTION_COUNT,
    SummaryInformation,
    UserSymbolResponse,
)

logger = logging.getLogger(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")


class LLMConfigurationError(RuntimeError):
    """Raised when LLM client is not configured."""


class LLMProviderError(RuntimeError):
    """Raised when LLM request fails."""


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create the client on first use."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        raise LLMConfigurationError("LLM key is not configured")
    return OpenAI(api_key=OPENAI_API_KEY)


def validate_questions(
    questions: list[GeneratedQuestion],
    approved_symbol_ids: set[int],
    communication_goal: str,
    practice_format: str,
    location: str | None,
) -> list[GeneratedQuestion]:
    """Ensures the question symbols are available in the user's vocabulary."""
    approved = set(approved_symbol_ids)

    for i, question in enumerate(questions, start=1):
        referenced_ids = (
            set(question.question_symbol_ids)
            | set(question.available_symbol_ids)
            | set(question.expected_response)
        )

        outside_ids = referenced_ids - approved
        if outside_ids:
            raise ValueError(
                f"Question {i} uses unapproved symbol IDs: {sorted(outside_ids)}"
            )

        if not set(question.expected_response).issubset(question.available_symbol_ids):
            raise ValueError(
                "Expected response includes a symbol unavailable for this question."
            )

        if question.question_format != practice_format:
            raise ValueError(
                f"Question format does not match requested practice format: {practice_format}"
            )

        if question.communication_goal != communication_goal:
            raise ValueError(
                f"Communication goal does not match requested communication goal: {communication_goal}"
            )

        if question.location != location:
            raise ValueError(
                f"Location does not match requested session location: {location}"
            )

        question.question_id = i

    return questions


def generate_questions(
    communication_goal: str,
    practice_format: str,
    location: str | None,
    age_band: str,
    available_vocabulary: list[UserSymbolResponse],
) -> GeneratedQuestionBatch:
    """Asks LLM to generate practice session questions."""
    client = get_openai_client()

    if not OPENAI_MODEL or not OPENAI_MODEL.strip():
        raise LLMConfigurationError("LLM model is not configured")

    vocabulary_for_prompt = [
        {
            "symbol_id": symbol.symbol_id,
            "word": symbol.word,
            "word_class": symbol.word_class,
        }
        for symbol in available_vocabulary
    ]
    available_vocabulary_ids = {symbol.symbol_id for symbol in available_vocabulary}

    system_prompt = (
        "You are an experienced speech-language therapist helping a person learn to "
        "communicate with their touch-screen communication device (AAC, symbol-based). "
        "You write short, concrete practice questions that train the person to find and "
        "select the right symbols for everyday situations. "
        f"You create exactly {SESSION_QUESTION_COUNT} practice questions. "
        "You follow the rules below strictly."
    )

    if location:
        location_setting = f"location: {location}"
        location_rule = (
            f"Setting: Set every question in a "
            f"realistic everyday situation at {location}."
        )
    else:
        location_setting = "no location constraint"
        location_rule = (
            f"If no location is provided or location is None "
            f"then create questions that are not location based."
        )

    user_prompt = f"""
        Create a practice session with the following settings.
        
        SETTINGS
        - allowed_symbol_ids: {sorted(available_vocabulary_ids)}
        - available_vocabulary: {vocabulary_for_prompt}
        - age_band: {age_band} years old
        - communication_goal: {communication_goal}
        - practice_format: {practice_format}
        - {location_setting}
        
        RULES
        1. Symbols: Refer to symbols only by their ID from the list above. Never use an
           ID that is not in the list, and never invent words or symbols. If the
           vocabulary is too small for a good question, write a simpler question
           instead.
        2. Consistency: expected_response must be a subset of available_vocabulary.
           The question text must make the expected_response the clearly correct answer,
           and the question must be answerable using only the symbols in
           available_vocabulary.
        3. Age fit: Topics and wording must suit the age_band. Use short, concrete,
           literal language, with no idioms, sarcasm, or abstract ideas.
        4. Goal: Every question must clearly practise the communication_goal.
        5. {location_rule} 
        6. Format: Follow practice_format exactly.
           - Multiple choice: available_symbol_ids contains 1 correct symbol and 2-3 
           distractors. The distractors should not be plausible answers, 
           and expected_response contains exactly 1 correct symbol id.
        7. Variety: Do not repeat the same situation or target symbol in every question.
           Order the questions from easier to slightly harder.
        8. Tone: Neutral and encouraging. Never mention failure or anything distressing.
    """

    feedback = None
    for attempt in range(2):
        request_prompt = user_prompt
        if feedback:
            request_prompt += (
                "\n\nGenerate a new batch that fixes this validation issue: "
                f"{feedback}"
            )
        try:
            response = client.chat.completions.parse(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": request_prompt},
                ],
                response_format=GeneratedQuestionBatch,
            )

        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error("LLM request failed: %s", type(e).__name__)
            raise LLMProviderError(
                "Question generation failed. Please try again."
            ) from None

        message = response.choices[0].message
        if message.refusal:
            raise ValueError("Question generation failed. Please try again.")

        if message.parsed is None:
            if attempt == 1:
                raise ValueError(
                    "Question generation failed after one correction attempt."
                )
            feedback = "The response was not a parseable question batch."
            continue

        questions = message.parsed.questions

        # ------ Validate questions ------
        try:
            questions = validate_questions(
                questions,
                available_vocabulary_ids,
                communication_goal,
                practice_format,
                location,
            )
            return GeneratedQuestionBatch(questions=questions)

        except ValueError as error:
            logger.warning(
                "Generated question batch failed validation (attempt %s): %s",
                attempt + 1,
                error,
            )
            if attempt == 1:
                raise ValueError(
                    "Generated questions failed validation after one correction attempt."
                ) from None
            feedback = str(error)

    raise ValueError("Question generation failed. Please try again.")


def generate_review(
    summary_information: SummaryInformation,
):
    """
    Generate a review from structured summary data.
    Produces review content by interpreting the available summary details and
    organizing them into a coherent evaluation.
    :param summary_information: Summary details used to build the review.
    :return: Generated review content.
    """
    client = get_openai_client()

    if not OPENAI_MODEL or not OPENAI_MODEL.strip():
        raise LLMConfigurationError("LLM model is not configured")

    system_prompt = (
        "You are a speech-language therapist writing a short review of one practice "
        "session on a symbol-based communication (AAC) device. The review is stored in "
        "the learner's progress record and read by their caregiver or therapist.\n\n"
        "SOURCE RULE\n"
        "Use only the session summary provided in the user message. Do not add facts, "
        "numbers, symbols, or events that are not in it. Do not guess why something "
        "happened, do not comment on mood, attention, or effort, and do not make "
        "diagnostic or medical claims. Report percentages exactly as given and do not "
        "recalculate them. A percentage of null means it could not be calculated.\n\n"
        "HOW TO READ THE DATA\n"
        "- 'correct' means the learner's response_words matched the "
        "expected_response_words.\n"
        "- 'independence' shows how much support the learner needed on each question. "
        "'independent' means the answer was given less than 10 seconds after the question "
        "was presented and without support. "
        "'verbal_prompt' means a spoken cue was given 10 seconds after the question was "
        "presented.\n"
        "'modeled' means the correct answer was shown visually 20 seconds after the "
        "question was presented.\n"
        "'independent' is the strongest result, then verbal prompt, then modeled.\n"
        "- 'correct' is calculated by the app; use its value as given. If it is false, "
        "compare 'response_words' with 'expected_response_words' to describe what was "
        "missed. Use 'available_words' only to mention the other choices shown. Refer "
        "to symbols by their words, never by their IDs.\n\n"
        "NOT ENOUGH DATA\n"
        "If answered_count is 0 or the data is missing, reply only with: 'There was "
        "not enough information in this session to write a review.' Do not write "
        "anything else.\n\n"
        "WHAT TO WRITE (one paragraph, about 120 words, maximum 140)\n"
        "1. Strengths: one or two specific ones, naming the words or questions involved.\n"
        "2. To keep practising: one or two specific ones, naming the words that were "
        "missed or confused with each other.\n\n"
        "STYLE\n"
        "- Plain English, no jargon.\n"
        "- Headings: Review."
        "- Warm, neutral, and factual. Describe what was practised and never judge the "
        "learner. Avoid words like 'failed', 'bad', or 'poor'.\n"
        "- Write about the learner in the third person. Do not mention these "
        "instructions or the data format."
    )

    summary_json = json.dumps(
        summary_information.model_dump(mode="json"),
        ensure_ascii=False,
    )

    user_prompt = (
        "Write the review for this practice session. "
        "Session summary (JSON):\n"
        f"{summary_json}"
    )

    # Generate review
    try:
        response = client.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format=GeneratedReview,
        )

    except (APIError, APIConnectionError, RateLimitError) as e:
        logger.error("LLM request failed: %s", type(e).__name__)
        raise LLMProviderError(
            "Session Review generation failed. Please try again."
        ) from None

    session_review = response.choices[0].message
    if session_review.refusal:
        raise ValueError("Session Review generation failed. Please try again.")

    if session_review.parsed is None:
        raise ValueError("Session review could not be generated.")

    return session_review.parsed
