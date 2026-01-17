resource "aws_iam_role_policy" "admin" {
  name = "admin_policy"
  role = aws_iam_role.app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # Full admin access!
        Resource = "*"
      }
    ]
  })
}