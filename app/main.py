import logging
# pyrefly: ignore [missing-import]
from fastapi import BackgroundTasks, FastAPI, status
from app.models import IncidentPayload, WebhookResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agentic-incident-flow")

app = FastAPI(
    title="Agentic Incident Flow on ServiceNow PDI",
    description="FastAPI webhook receiver for ServiceNow incidents with AI triage agent",
    version="1.0.0",
)


def mock_process_incident(payload: IncidentPayload):
    """Temporary worker function to simulate background incident processing."""
    logger.info("=" * 60)
    logger.info(" [DEMO WORKER] Starting processing for Incident: %s", payload.number)
    logger.info("   • Sys ID:           %s", payload.incident_sys_id)
    logger.info("   • Short Description: %s", payload.short_description)
    logger.info("   • Description:       %s", payload.description or "(Empty)")
    logger.info("   • Priority:          %s", payload.priority)
    logger.info("=" * 60)


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
    background_tasks.add_task(mock_process_incident, payload)

    return WebhookResponse(
        status="accepted",
        incident=payload.number,
        message="Incident accepted for agentic triage",
    )