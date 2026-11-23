# CPU saturation runbook

1. Confirm the affected service, host, and alert time window.
2. Review CPU utilization, load average, process-level metrics, request rate, and recent deployments.
3. Compare replicas and availability-zone patterns to identify whether impact is isolated.
4. Check for traffic spikes, expensive queries, runaway jobs, and resource-limit changes.
5. Escalate to the service owner before any restart, scaling, or configuration change.

**Safety:** This runbook is guidance only. Any infrastructure-changing action requires an authorized operator and the normal change process.
