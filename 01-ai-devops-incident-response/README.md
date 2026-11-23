# AI DevOps Incident Response Assistant

FastAPI service that accepts Prometheus-style webhook/test alerts, persists incidents, retrieves Markdown runbooks, produces AI-assisted or deterministic analysis, and records human approval decisions. **It does not execute remediation.**

## API walkthrough

1. `POST /alerts` with `{"alert_name":"CPUHigh","severity":"warning","summary":"CPU above 90% for 10 minutes"}`.
2. `POST /incidents/{id}/analyze` with `{"include_ai":true}`. Without `OPENAI_API_KEY`, deterministic fallback is used.
3. `GET /incidents/{id}` to inspect analysis and audit history.
4. `POST /incidents/{id}/approval` with `{"decision":"approved","note":"Reviewed dashboard and runbook"}` and header `X-Actor: operator-name`.
5. `GET /incidents/{id}/audit` to review decisions.

Webhook endpoint: `POST /webhooks/alert`. Set `ALERT_WEBHOOK_TOKEN` and send it in `X-Webhook-Token` before exposing the endpoint outside a local demo.

## Local run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -q
```

For production, add SSO/OIDC, role-based authorization, secret rotation, rate limiting, schema migrations, retention policy, private networking, TLS, and a formal change-management integration. Do not use the demo `X-Actor` header as production identity proof.
