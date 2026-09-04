import json
import logging
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types

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

logger = logging.getLogger("agentic-incident-flow")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
        logger.info("Gemini client initialized (model: %s)", settings.gemini_model)
    return _client

def get_agent_decision(
    short_description: str,
    description: str,
) -> AgentDecision:
    user_turn = build_user_turn(
        short_description=short_description,
        description=description,
    )

    try:
        client = _get_client()
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

        decision = AgentDecision.model_validate_json(raw)
        logger.info(
            "Gemini decision: %s | reasoning: %s",
            decision.decision,
            decision.reasoning,
        )
        return decision

    except Exception as exc:
        logger.error(
            "Gemini call failed — falling back to escalate. Error: %s",
            exc,
            exc_info=True,
        )
        return AgentDecision(
            reasoning=DEFAULT_FALLBACK_REASONING,
            decision=DEFAULT_FALLBACK_DECISION,
            message=DEFAULT_FALLBACK_MESSAGE,
        )
