# ---------------------------------------------------------------------------
# LLM / Gemini Generation Constants
# ---------------------------------------------------------------------------
GEMINI_TEMPERATURE: float = 0.0
GEMINI_RESPONSE_MIME_TYPE: str = "application/json"

DEFAULT_FALLBACK_DECISION: str = "escalate"
DEFAULT_FALLBACK_REASONING: str = (
    "Agent encountered an unexpected error and could not evaluate the incident."
)
DEFAULT_FALLBACK_MESSAGE: str = (
    "We were unable to automatically process your request at this time. "
    "Your ticket has been escalated to the IT support team who will follow up shortly."
)

# ---------------------------------------------------------------------------
# Agent Triage Decisions
# ---------------------------------------------------------------------------
DECISION_RESPOND: str = "respond"
DECISION_ASK: str = "ask"
DECISION_ESCALATE: str = "escalate"

SN_STATE_RESOLVED: str = "6"
SN_CLOSE_CODE_SOLVED_PERMANENTLY: str = "Solved (Permanently)"
