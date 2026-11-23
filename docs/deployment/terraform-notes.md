# Terraform deployment notes

The `01-ai-devops-incident-response/infra/terraform` directory contains a small AWS foundation example for a private encrypted S3 bucket used to store non-sensitive runbook/artifact backups. It is not the full application hosting stack. Extend only after selecting region, VPC strategy, ECS/EKS, ALB, RDS, IAM boundaries, DNS, TLS, logging, backups, and environment separation. Run `terraform fmt`, `terraform validate`, and security scanning before applying. Never commit state files or credentials.
