import time
import warnings
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types

warnings.filterwarnings("ignore", category=UserWarning)



from app.config.constants import (
    DEFAULT_FALLBACK_DECISION,
    DEFAULT_FALLBACK_MESSAGE,
    DEFAULT_FALLBACK_REASONING,
    GEMINI_RESPONSE_MIME_TYPE,
    GEMINI_TEMPERATURE,
)
from app.config.settings import settings
from app.models import AgentDecision
from app.prompts.prompts import SYSTEM_PROMPT, build_user_turn


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def get_agent_decision(
    short_description: str,
    description: str,
    max_retries: int = 3,
    retry_delay: float = 1.5,
) -> AgentDecision:
    user_turn = build_user_turn(
        short_description=short_description,
        description=description,
    )

    client = _get_client()

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=user_turn,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type=GEMINI_RESPONSE_MIME_TYPE,
                    response_schema=AgentDecision,
                    temperature=GEMINI_TEMPERATURE,
                ),
            )

            raw = response.text
            return AgentDecision.model_validate_json(raw)

        except Exception as exc:
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue

            print(f"[ERROR] Gemini triage failed after {max_retries} retries: {exc}")
            return AgentDecision(
                reasoning=DEFAULT_FALLBACK_REASONING,
                decision=DEFAULT_FALLBACK_DECISION,
                message=DEFAULT_FALLBACK_MESSAGE,
            )


