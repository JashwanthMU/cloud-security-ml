resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  user_data = <<-EOF
              #!/bin/bash
              export DB_PASSWORD="SuperSecret123"
              export API_KEY="1234567890abcdef"
              EOF
}