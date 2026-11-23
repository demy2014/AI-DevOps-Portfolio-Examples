# Local deployment

1. Copy `.env.example` to `.env`.
2. Replace the demo database and Grafana passwords.
3. Optionally set `OPENAI_API_KEY` and `OPENAI_MODEL`.
4. Run `docker compose up --build`.
5. Check `http://localhost:8001/health`, `http://localhost:8002/health`, and each `/docs` page.
6. Stop with `docker compose down`; preserve data with the named `pgdata` volume. To reset demo data only, use `docker compose down -v` (destructive).

For cloud deployment, use managed PostgreSQL, private networking, an HTTPS ingress/load balancer, workload IAM roles, secret manager, container registry, and separate environments. Terraform directory is a starter, not a production-ready landing zone.
