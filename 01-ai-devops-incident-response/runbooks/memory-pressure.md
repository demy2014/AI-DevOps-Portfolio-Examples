# Memory pressure runbook

1. Confirm host/container memory, working set, limits, and OOM events.
2. Check recent deploys, workload volume, and memory trend by process or pod.
3. Review application logs for allocation failures or leak indicators.
4. Compare healthy replicas and inspect autoscaling events.
5. Escalate to the service owner before restart, rescheduling, or resource-limit changes.
