# data/raw/risky/example_001.tf
resource "aws_s3_bucket" "data" {
  bucket = "customer-database-backup"
  acl    = "public-read"  # RISKY!
  
  # No encryption
  # No versioning
}