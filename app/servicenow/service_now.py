import logging
from typing import Any
# pyrefly: ignore [missing-import]
import httpx

from app.config.constants import (
    DECISION_ASK,
    DECISION_ESCALATE,
    DECISION_RESPOND,
    SN_CLOSE_CODE_SOLVED_PERMANENTLY,
    SN_STATE_RESOLVED,
)
from app.config.settings import settings
from app.models import AgentDecision

logger = logging.getLogger("agentic-incident-flow")


def build_update_payload(decision: AgentDecision) -> dict[str, Any]:
    if decision.decision == DECISION_RESPOND:
        return {
            "state": SN_STATE_RESOLVED,
            "close_code": SN_CLOSE_CODE_SOLVED_PERMANENTLY,
            "close_notes": decision.message,
            "work_notes": decision.message,
        }
    elif decision.decision == DECISION_ASK:
        return {
            "comments": decision.message,
        }
    elif decision.decision == DECISION_ESCALATE:
        return {
            "work_notes": f"[Escalated by AI Agent]\nReason: {decision.reasoning}\n\n{decision.message}",
        }
    return {
        "work_notes": decision.message,
    }


def update_incident(
    incident_sys_id: str,
    decision: AgentDecision,
    timeout: float = 10.0,
) -> dict[str, Any]:
    url = f"{settings.sn_instance_url.rstrip('/')}/api/now/table/incident/{incident_sys_id}"
    payload = build_update_payload(decision)

    with httpx.Client(timeout=timeout) as client:
        response = client.patch(
            url=url,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            auth=(settings.sn_username, settings.sn_password),
        )
        response.raise_for_status()
        logger.info("Updated ServiceNow incident %s (decision: %s)", incident_sys_id, decision.decision)
        return response.json().get("result", {})
