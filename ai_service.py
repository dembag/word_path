import os
from functools import lru_cache
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError


from api_schemas import SESSION_QUESTION_COUNT

logger = logging.getLogger(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")


class LLMConfigurationError(RuntimeError):
    """Raised when LLM client is not configured."""


class LLMProviderError(RuntimeError):
    """Raised when LLM request fails."""


class QuestionDraft(BaseModel):
    question: str
    question_symbols: list[int] = Field(min_length=1)
    available_symbols: list[int] = Field(min_length=1)
    target_symbols: list[int] = Field(min_length=1)


class SessionQuestions(BaseModel):
    questions: list[QuestionDraft]


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create the client on first use."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        raise LLMConfigurationError("LLM key is not configured")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_questions(prompt: str) -> list[QuestionDraft]:
    """Asks LLM to generate practice session questions."""
    client = get_openai_client()
    if not OPENAI_MODEL or not OPENAI_MODEL.strip():
        raise LLMConfigurationError("LLM model is not configured")
    try:
        response = client.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You create exactly {SESSION_QUESTION_COUNT} practice questions.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=SessionQuestions,
        )
    except (APIError, APIConnectionError, RateLimitError) as e:
        logger.error("LLM request failed: %s", type(e).__name__)
        raise LLMProviderError(
            "Question generation failed. Please try again."
        ) from None
    message = response.choices[0].message
    if message.refusal or message.parsed is None:
        raise ValueError("Question generation failed. Please try again.")

    return message.parsed.questions
