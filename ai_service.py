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
from word_path.data_models import Symbol

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


def validate_question_symbols(
    questions: list[GeneratedQuestion],
    approved_symbol_ids: set[int],
) -> None:
    """Ensures the question symbols are available in the user's vocabulary."""
    approved = set(approved_symbol_ids)

    for question in questions:
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


def generate_questions(
    communication_goal: str,
    practice_format: str,
    location: str,
    age_band: str,
    available_vocabulary: list[UserSymbolResponse],
) -> list[GeneratedQuestion]:
    """Asks LLM to generate practice session questions."""
    client = get_openai_client()

    if not OPENAI_MODEL or not OPENAI_MODEL.strip():
        raise LLMConfigurationError("LLM model is not configured")

    available_vocabulary_ids = {symbol.symbol_id for symbol in available_vocabulary}

    system_prompt = (
        "You are a speech therapist helping someone learn how to communicate"
        "using their touch-screen communication device."
        f"You create exactly {SESSION_QUESTION_COUNT} practice questions."
        "You must follow the instructions."
    )

    user_prompt = (
        "Instructions: "
        "- Use only the "
        f"available_vocabulary: {available_vocabulary}"
        f"age_band: {age_band} years old"
        f"communication_goal: {communication_goal}"
        f"practice_format: {practice_format}"
        f"location: {location}"
    )

    feedback = None
    for attempt in range(2):
        request_prompt = prompt
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
                    {
                        "role": "user",
                        "content": user_prompt
                    },
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
        try:
            validate_question_symbols(questions, available_vocabulary_ids)
            return questions
        except ValueError as error:
            if attempt == 1:
                raise ValueError(
                    "Generated questions failed validation after one correction attempt."
                ) from None
            feedback = str(error)

    raise ValueError("Question generation failed. Please try again.")
