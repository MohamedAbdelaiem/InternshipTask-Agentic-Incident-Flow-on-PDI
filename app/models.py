from typing import Literal, Optional
from pydantic import BaseModel, Field


class IncidentPayload(BaseModel):
    """Payload received from ServiceNow Business Rule via POST /webhook."""

    incident_sys_id: str = Field(..., description="ServiceNow sys_id of the incident record")
    number: str = Field(..., description="Incident number, e.g. INC0010001")
    short_description: str = Field(..., description="One-line summary typed by the user")
    description: Optional[str] = Field(default="", description="Detailed description of the issue")
    priority: int = Field(default=3, description="Priority integer from 1 (highest) to 5 (lowest)")


class AgentDecision(BaseModel):
    """Structured decision output produced by Gemini."""

    decision: Literal["respond", "ask", "escalate"] = Field(
        ...,
        description="Action decision: respond (solution found), ask (vague/missing info), or escalate (out of scope/human needed)",
    )
    message: str = Field(
        ...,
        description="The direct solution, clarifying question, or escalation reason",
    )


class WebhookResponse(BaseModel):
    status: str = "accepted"
    incident: str
    message: str = "Incident accepted for agentic triage"
