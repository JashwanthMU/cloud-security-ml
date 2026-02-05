resource "aws_s3_bucket" "secure_data" {
  bucket = "company-secure-data"
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
  
  logging {
    target_bucket = "company-logs"
    target_prefix = "s3-access-logs/"
  }
  
  tags = {
    Environment = "production"
    Compliance  = "HIPAA"
  }
}