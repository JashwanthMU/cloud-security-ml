resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  # No security group specified
  # No IAM role
  # Public IP
  associate_public_ip_address = true
  
  user_data = <<-EOF
              #!/bin/bash
              export DB_PASSWORD="hardcoded_password"
              EOF
              
  # No encryption on root volume
}