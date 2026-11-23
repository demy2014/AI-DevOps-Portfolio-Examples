# AI Lead Generation Agent

A review-first lead intake and qualification API. It validates email syntax, rejects duplicate emails, scores only explicitly supplied business attributes, optionally summarizes supplied data with an LLM, and records a human review. It does not scrape websites or send outreach.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
pytest -q
```

Open `/docs` for the API. The static demo UI is in `frontend/index.html`; serve it from the API's static mount in a future UI iteration or open it locally and configure the API origin.

## API

- `POST /leads` — create and score a lead.
- `POST /leads/import-csv` — import CSV (UTF-8, max 2 MB; required headers: `company,email`).
- `GET /leads` and `GET /leads?priority=high` — list.
- `POST /leads/{id}/summarize` — optional AI summary of supplied fields only.
- `POST /leads/{id}/review` — human review (`qualified`, `disqualified`, `contacted`).
- `GET /reports/summary` — transparent count-based metrics.

Scoring weights are documented in `score_lead()` and are intentionally simple/configurable. Treat score as prioritization assistance, not a prediction of purchase intent. Before connecting a real CRM, add OAuth, least-privilege scopes, idempotency, field mapping, consent checks, and an explicit operator confirmation step.
