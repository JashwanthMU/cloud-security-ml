resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  
  map_public_ip_on_launch = false
  
  tags = {
    Name = "Private Subnet"
    Tier = "Private"
  }
}