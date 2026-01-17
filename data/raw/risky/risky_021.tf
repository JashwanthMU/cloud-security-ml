resource "aws_s3_bucket" "data" {
  bucket = "company-financial-records"
  # No ACL specified (defaults based on account settings)
  # No encryption
  # No versioning
  # No MFA delete
}