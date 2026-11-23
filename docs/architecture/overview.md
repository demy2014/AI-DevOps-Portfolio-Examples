# Portfolio architecture

```mermaid
flowchart LR
  A[Prometheus / Webhook] --> B[Incident FastAPI]
  B --> C[(PostgreSQL)]
  B --> D[Markdown Runbooks]
  B --> E[LLM or deterministic fallback]
  E --> F[Human approval + audit]
  G[CSV / Form / API] --> H[Lead FastAPI]
  H --> I[Transparent scoring]
  H --> J[Optional LLM summary]
  H --> K[(PostgreSQL)]
  H --> L[Human review / mock CRM handoff]
  B --> M[Prometheus / Grafana]
  H --> M
```

Services share a local PostgreSQL instance in Compose but own separate tables and API processes. Split databases and credentials for production. AI providers are optional and have deterministic fallback behavior.
