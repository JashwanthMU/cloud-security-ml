resource "aws_s3_bucket" "uploads" {
  bucket = "user-uploaded-files-prod"
  acl    = "public-read-write"
  
  # No encryption
  # No versioning
  # No logging
}