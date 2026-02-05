resource "aws_iam_user" "admin_user" {
  name = "admin"
  path = "/"
  
  # No MFA required!
  
  tags = {
    Role = "Administrator"
  }
}