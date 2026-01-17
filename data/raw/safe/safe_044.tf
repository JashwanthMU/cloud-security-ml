resource "aws_s3_bucket" "website" {
  bucket = "company-public-website"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

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

  tags = {
    Purpose     = "Public Website"
    Public      = "Intentional"
    Environment = "Production"
  }
}