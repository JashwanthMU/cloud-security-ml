resource "aws_s3_bucket" "logs" {
  bucket = "application-logs-bucket"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true
    expiration {
      days = 90
    }
  }

  tags = {
    Environment = "Production"
    Purpose     = "Application Logs"
  }
}