resource "aws_s3_bucket" "runbook_artifacts" {
  bucket_prefix = "${var.project_name}-runbooks-"
  force_destroy = false
  tags = { Project = var.project_name, ManagedBy = "Terraform" }
}
resource "aws_s3_bucket_versioning" "runbook_artifacts" {
  bucket = aws_s3_bucket.runbook_artifacts.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "runbook_artifacts" {
  bucket = aws_s3_bucket.runbook_artifacts.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
}
resource "aws_s3_bucket_public_access_block" "runbook_artifacts" {
  bucket = aws_s3_bucket.runbook_artifacts.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
output "runbook_bucket_name" { value = aws_s3_bucket.runbook_artifacts.bucket }
