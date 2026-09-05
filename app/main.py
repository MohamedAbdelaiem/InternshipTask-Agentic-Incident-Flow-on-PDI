# pyrefly: ignore [missing-import]
from fastapi import BackgroundTasks, FastAPI, status
from app.llm.gemeni import get_agent_decision
from app.models import IncidentPayload, WebhookResponse
from app.servicenow import update_incident

_processed_incidents: set[str] = set()

app = FastAPI(
    title="Agentic Incident Flow on ServiceNow PDI",
    description="FastAPI webhook receiver for ServiceNow incidents with AI triage agent",
    version="1.0.0",
)


def process_incident(payload: IncidentPayload):
    if payload.incident_sys_id in _processed_incidents:
        return

    try:
        decision = get_agent_decision(
            short_description=payload.short_description,
            description=payload.description or "",
        )
        update_incident(payload.incident_sys_id, decision)
        _processed_incidents.add(payload.incident_sys_id)
    except Exception as exc:
        _processed_incidents.discard(payload.incident_sys_id)
        print(f"[ERROR] Failed processing incident {payload.number}: {exc}")



@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Agentic Incident Flow Webhook",
        "endpoints": {
            "webhook": "POST /webhook",
            "docs": "/docs",
        },
    }


@app.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Webhook"],
)
async def receive_incident(
    payload: IncidentPayload,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(process_incident, payload)

    return WebhookResponse(
        status="accepted",
        incident=payload.number,
        message="Incident accepted for agentic triage",
    )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="error")

