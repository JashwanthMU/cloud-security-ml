resource "aws_security_group" "rdp_access" {
  name = "rdp_access"
  
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}