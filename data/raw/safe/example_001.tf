# data/raw/safe/example_001.tf
resource "aws_s3_bucket" "website" {
  bucket = "company-marketing-site"
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
  
  tags = {
    Purpose = "Website hosting"
    Public  = "Yes - intentional"
  }
}