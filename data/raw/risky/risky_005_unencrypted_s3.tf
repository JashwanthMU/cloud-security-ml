resource "aws_s3_bucket" "sensitive_data" {
  bucket = "financial-records-2024"
  acl    = "private"
  # No encryption!
}