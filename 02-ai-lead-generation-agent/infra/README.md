# Lead agent cloud deployment plan

Recommended first AWS deployment: ECR + ECS Fargate services behind an HTTPS ALB, private subnets, RDS PostgreSQL, Secrets Manager, task IAM roles, CloudWatch logs/alarms, WAF, and GitHub Actions OIDC. Keep CRM credentials in Secrets Manager and use least-privilege OAuth scopes. Do not expose the database publicly. Terraform implementation is intentionally left as a design task until the target AWS account, network, DNS, and cost limits are confirmed.
