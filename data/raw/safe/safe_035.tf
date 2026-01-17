resource "aws_instance" "app" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_class = "t3.micro"
  
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.app.id]
  
  iam_instance_profile = aws_iam_instance_profile.app.name
  
  user_data = file("${path.module}/user_data.sh")
  
  root_block_device {
    encrypted   = true
    volume_size = 20
  }

  metadata_options {
    http_tokens = "required"  # IMDSv2
  }

  tags = {
    Name        = "Application Server"
    Environment = "Production"
  }
}