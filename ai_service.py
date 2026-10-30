import os
from functools import lru_cache
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError


from api_schemas import (
    GeneratedQuestion,
    GeneratedQuestionBatch,
    SESSION_QUESTION_COUNT,
)
from api_schemas import UserSymbolResponse


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

        if not referenced_ids.issubset(approved):
            raise ValueError(
                "Generated question uses symbols outside the learner's vocabulary."
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
) -> list[GeneratedQuestion]:
    """Asks LLM to generate practice session questions."""
    client = get_openai_client()

    if not OPENAI_MODEL or not OPENAI_MODEL.strip():
        raise LLMConfigurationError("LLM model is not configured")

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
        - available_vocabulary: {available_vocabulary}
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
             plausible distractors, and expected_response contains exactly 1 correct symbol id.
           - Free selection: available_symbol_ids contains the symbols that make sense
             for the situation, and expected_response lists the correct symbol(s).
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

            return questions
        except ValueError as error:
            if attempt == 1:
                raise ValueError(
                    "Generated questions failed validation after one correction attempt."
                ) from None
            feedback = str(error)

    raise ValueError("Question generation failed. Please try again.")
