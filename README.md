# Agentic Incident Flow on ServiceNow PDI

An automated IT support triage flow integrating a **ServiceNow Developer Instance (PDI)**, a **FastAPI** webhook receiver, and **Google Gemini** for agentic incident evaluation and closed-loop ticket write-back.

> 🎬 **Live Demo Video**: [Watch the Live Loop Demonstration on Google Drive](https://drive.google.com/file/d/18_ef4ZSV7RTnx4FMUkH-YVfIquSC4-9n/view?usp=sharing)  
> Verifiable proof of the autonomous triage loop running end-to-end on ServiceNow PDI across all 3 decision paths (`respond`, `ask`, and `escalate`).

---

## Overview

When an incident is created in ServiceNow, this service autonomously processes and acts on it without manual intervention:

```
┌─────────────────┐       (1) Incident Created       ┌──────────────────┐
│  ServiceNow PDI │ ───────────────────────────────> │  Business Rule   │
└─────────────────┘                                  └─────────┬────────┘
        ▲                                                      │ (2) POST /webhook
        │                                                      ▼
        │ (4) PATCH Incident                         ┌──────────────────┐
        │     - respond: Resolve + Close Notes       │  FastAPI Service │
        │     - ask: Customer Comment                │  (Background Task)
        │     - escalate: Internal Work Note         └─────────┬────────┘
        │                                                      │ (3) Triage Prompt
        │                                                      ▼
        │                                            ┌──────────────────┐
        └─────────────────────────────────────────── │  Google Gemini   │
                                                     │  (5 KB Articles) │
                                                     └──────────────────┘
```

1. **Ticket Creation**: A user opens an incident in ServiceNow.
2. **Event Capture**: An asynchronous Business Rule fires on `insert` and sends the incident payload to the FastAPI `/webhook` endpoint.
3. **AI Triage**: The service evaluates the incident using Gemini with strict knowledge boundary enforcement over 5 predefined KB articles.
4. **Write-Back**: The service updates the incident in ServiceNow via the REST Table API.

---

## Decision Logic & Write-Back Contract

The agent strictly maps the incident into one of three decisions:

| Decision | Trigger Criteria | ServiceNow Write-Back Action |
| :--- | :--- | :--- |
| **`respond`** | A KB article directly solves the problem, and sufficient context is provided. | Sets `state: 6` (Resolved), `close_code: "Solved (Permanently)"`, `close_notes`, and `work_notes` with the solution. |
| **`ask`** | An issue relates to a KB article, but the description is vague or missing error details. | Posts a clarifying question to `comments` (customer-visible), leaving the incident open for the user to reply. |
| **`escalate`** | The issue is outside the KB scope, was already attempted without success, or requires human intervention. | Adds an internal note to `work_notes` indicating escalation to the IT support team. |

### Knowledge Boundary (5 KB Articles)
1. **Printer not printing**: Restart the printer and unplug the cable for 30 seconds.
2. **Email not sending**: Check SMTP settings and ensure port 587 is open.
3. **Cannot access system**: Reset password via the 'Forgot Password' page.
4. **Slow network**: Restart the router and check cable connections.
5. **Browser pages not loading**: Clear cache and try incognito mode.

---

## Project Structure

```
Agentic-Incident-Flow-on-PDI/
├── app/
│   ├── config/
│   │   ├── constants.py       # Triage decisions, ServiceNow state codes, defaults
│   │   └── settings.py        # Pydantic Settings reading .env
│   ├── llm/
│   │   └── gemeni.py          # Gemini client, retry logic, structured output
│   ├── prompts/
│   │   └── prompts.py         # System prompt, KB boundary rules, user turn builder
│   ├── servicenow/
│   │   └── service_now.py     # ServiceNow REST client (PATCH incident write-back)
│   ├── models.py              # Pydantic schemas (IncidentPayload, AgentDecision)
│   └── main.py                # FastAPI server and background task worker
├── tests/
│   ├── payload_contract.json  # Schema documentation of webhook input
│   ├── test_incidents.json    # Canonical test cases (respond, ask, escalate)
│   └── test_agent.py          # Automated verification script
├── business_rule.js           # ServiceNow Business Rule script
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment variables
├── .gitignore                 # Excludes .env, .venv, caches
└── README.md                  # Project documentation
```

---

## Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **uv** (recommended) or standard **pip**
- A free **ServiceNow Personal Developer Instance (PDI)** from [developer.servicenow.com](https://developer.servicenow.com)
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **ngrok** for exposing your local webhook to ServiceNow

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/MohamedAbdelaiem/Agentic-Incident-Flow-on-PDI.git
cd Agentic-Incident-Flow-on-PDI

# Create and activate virtual environment
uv venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate  # On macOS/Linux

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# ServiceNow PDI Instance Configuration
SN_INSTANCE_URL=https://devXXXXXX.service-now.com
SN_USERNAME=admin
SN_PASSWORD=your_pdi_admin_password

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

> **Important Note for ServiceNow PDIs**:
> Recent ServiceNow releases (Xanadu / Washington) enforce Basic Auth Restrictions. Ensure the `admin` account (or your API user) has the **`snc_basic_auth_api_access`** role assigned in `sys_user_has_role`.

---

## Running the Service

### Step 1 — Start the FastAPI Service
```bash
uv run python -m app.main
```
The server will start at `http://localhost:8000`. Health check is available at `GET /`.

### Step 2 — Expose Locally via ngrok
In a separate terminal, expose port 8000:
```bash
ngrok http 8000
```
Copy the generated public URL (e.g., `https://abc1234.ngrok-free.app`).

### Step 3 — Configure the ServiceNow Business Rule
1. In your PDI, navigate to **System Definition > Business Rules** and click **New**.
2. Fill in:
   - **Name**: `Task0 - Send Incident to Agent`
   - **Table**: `Incident [incident]`
   - **Advanced**: Checked
   - **When to run**: When = `after`, check **Insert**
3. Switch to the **Advanced** tab and paste the script from `business_rule.js`.
4. Replace `YOUR_ENDPOINT` with your ngrok URL:
   ```javascript
   var url = "https://abc1234.ngrok-free.app/webhook";
   ```
5. Click **Submit**.

---

## Verification & Testing

### Demo Video (PDI Live Proof)
A complete video demonstration verifying the autonomous end-to-end loop running live against a ServiceNow Personal Developer Instance (PDI):
- 📺 **Direct Link**: [ServiceNow PDI Live Loop Demo (Google Drive)](https://drive.google.com/file/d/18_ef4ZSV7RTnx4FMUkH-YVfIquSC4-9n/view?usp=sharing)
- **Highlights Covered**: Real-time webhook triggering from ServiceNow Business Rules, Gemini triage with KB boundary enforcement, and REST Table API write-backs for `respond`, `ask`, and `escalate`.

### Automated Test Suite
Run the test suite against the canonical incidents:
```bash
uv run python tests/test_agent.py
```

Expected output:
```text
Testing Official Incidents (Decision + ServiceNow Payload):

[PASS] Ticket 1: Printer not printing after office move
       Decision : respond (Expected: respond)
       Message  : Please restart the printer and unplug the cable for 30 seconds...
       Payload  : {'state': '6', 'close_code': 'Solved (Permanently)', ...}

[PASS] Ticket 2: Cannot send email
       Decision : ask (Expected: ask)
       Message  : Could you please provide your email client and error message...
       Payload  : {'comments': '...'}

[PASS] Ticket 3: Request: annual leave approval
       Decision : escalate (Expected: escalate)
       Message  : Your ticket regarding annual leave approval has been escalated...
       Payload  : {'work_notes': '...'}

All 3 tests and ServiceNow payloads verified!
```

### Manual Verification in ServiceNow
1. Open your PDI and click **Incident > Create New**.
2. Create incidents with the following descriptions:
   - **Test 1**: Short description: `Printer not printing after office move`, Description: `It was working yesterday. I tried turning it off and on.` $\rightarrow$ **Ticket is automatically Resolved**.
   - **Test 2**: Short description: `Cannot send email`, Description: `It just doesn't work.` $\rightarrow$ **Clarifying question added to Comments**.
   - **Test 3**: Short description: `Request: annual leave approval`, Description: `I would like to take next week off.` $\rightarrow$ **Internal escalation note added to Work Notes**.

---

## Features & Reliability

- **Fast Webhook Acknowledgement**: `/webhook` responds with `202 Accepted` in $<50$ms. Heavy LLM calls run in FastAPI background workers.
- **Idempotency Guard**: Deduplication set prevents duplicate processing if webhooks are retried.
- **Automatic Retries**: Implements exponential backoff against Google Gemini transient `503 Service Unavailable` and `429 Rate Limit` responses.
- **Fallback Protection**: If LLM calls fail after all retries, incidents gracefully default to `escalate` so tickets are never lost.
