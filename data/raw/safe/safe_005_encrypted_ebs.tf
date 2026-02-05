resource "aws_ebs_volume" "secure_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  
  encrypted  = true
  kms_key_id = aws_kms_key.ebs_key.arn
  
  tags = {
    Name = "Encrypted Data Volume"
  }
}