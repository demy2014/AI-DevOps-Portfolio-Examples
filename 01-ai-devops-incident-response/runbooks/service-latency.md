# Service latency and elevated errors runbook

1. Check request rate, p50/p95/p99 latency, 4xx/5xx rates, and saturation.
2. Inspect database, cache, queue, DNS, and upstream dependency health.
3. Compare the alert start time with releases, config changes, and traffic shifts.
4. Correlate traces and structured logs using request or trace IDs.
5. Escalate before rollback, failover, or any production change.
