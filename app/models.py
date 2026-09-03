from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class IncidentPayload(BaseModel):
    """Payload received from ServiceNow Business Rule via POST /webhook."""

    model_config = ConfigDict(extra="ignore")

    incident_sys_id: str = Field(..., description="ServiceNow sys_id")
    number: str = Field(..., description="Incident number (e.g., INC0010001)")
    short_description: str = Field(..., description="Summary typed by user")
    description: Optional[str] = Field(default="", description="Detailed issue text")
    priority: int = Field(default=3, ge=1, le=5, description="Priority (1-5)")


class AgentDecision(BaseModel):
    """Structured routing and response decision for user inquiry."""

    reasoning: str = Field(
        ...,
        description=(
            "1-2 sentences analyzing the short_description and description to "
            "determine if the issue is actionable, incomplete, or out of scope."
        ),
    )
    decision: Literal["respond", "ask", "escalate"] = Field(
        ...,
        description=(
            "Action to take: "
            "'respond' = sufficient information available to provide a resolution or workaround; "
            "'ask' = user request is ambiguous, missing required logs, error codes, or context; "
            "'escalate' = requires physical access, admin credentials, vendor escalation, or P1 handling."
        ),
    )
    message: str = Field(
        ...,
        description=(
            "End-user facing text to be appended to ServiceNow Additional Comments: "
            "If 'respond': clear step-by-step troubleshooting steps or solution. "
            "If 'ask': concise clarification question targeting the missing piece. "
            "If 'escalate': polite confirmation acknowledging the issue and stating it has been reassigned to IT support."
        ),
    )


class WebhookResponse(BaseModel):
    status: str = "accepted"
    incident: str
    message: str = "Incident accepted for agentic triage"