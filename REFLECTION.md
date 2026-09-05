# Reflection: Task 0 — Agentic Incident Flow on ServiceNow PDI

### 1. What was the hardest part?

The most challenging part was working with ServiceNow’s security model and the LLM’s decision boundaries. Since the documentation and AI tools were not very helpful, I had to spend significant time investigating, testing, and learning through trial and error.

- **ServiceNow REST Authentication & Data Policies:**
  - In modern ServiceNow releases, Basic Authentication is restricted by default through platform security settings (`glide.authenticate.basic_auth.restriction.enforce = true`). Even with valid `admin` credentials that worked seamlessly in the browser UI, inbound REST API calls were rejected with `401 Unauthorized` until the account was explicitly assigned the specialized `snc_basic_auth_api_access` platform role.

### 2. What would you improve with more time?

I would improve the system in these areas:

1. **Persistent Queue & Deduplication**

   * Replace the in-memory `set` with **Redis** or a message queue to prevent duplicate processing and make the system more reliable when running multiple workers.

2. **Multi-Turn Conversations**

   * Make the agent listen to updates and user replies in the incident comments. This would allow it to continue the conversation after asking for more information.

3. **Dynamic Knowledge Retrieval (RAG)**

   * Replace the fixed 5 articles with **Qdrant** connected to ServiceNow's Knowledge Base, allowing the agent to search thousands of relevant articles.

4. **Better Monitoring**

   * Add tools like **OpenTelemetry** and **Grafana** to monitor response time, token usage, errors, and the agent's decisions (`respond` / `ask` / `escalate`).

