# This is Terraform - a language to define cloud resources
# Think of it like a recipe for creating AWS resources

# Example 1: Create an S3 bucket (like a folder in the cloud)
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-app-data"           # Name of the bucket
  acl    = "private"                # Who can access: private or public
  
  tags = {
    Environment = "production"      # Label: this is for production
    Team        = "engineering"     # Label: engineering team owns this
  }
}

# Example 2: Create a database
resource "aws_db_instance" "my_database" {
  identifier           = "myapp-db"
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  allocated_storage    = 20
  username             = "admin"
  password             = "mypassword"   # ← BAD! Password visible
  publicly_accessible  = true           # ← RISKY! Database exposed to internet
  storage_encrypted    = false          # ← RISKY! No encryption
}

# Example 3: Security Group (firewall rules)
resource "aws_security_group" "allow_ssh" {
  name = "allow_ssh"
  
  ingress {
    from_port   = 22                    # SSH port
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]         # ← RISKY! Open to entire internet
  }
}