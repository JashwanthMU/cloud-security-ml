"""
Creates 100 sample Terraform files
50 safe + 50 risky 
"""

import os

# Safe examples
safe_examples = [
    # S3 - Private with encryption
    '''resource "aws_s3_bucket" "logs" {
  bucket = "application-logs-bucket"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true
    expiration {
      days = 90
    }
  }

  tags = {
    Environment = "Production"
    Purpose     = "Application Logs"
  }
}''',

    # RDS - Encrypted private database
    '''resource "aws_db_instance" "main" {
  identifier           = "myapp-database"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true
  
  username             = "admin"
  password             = var.db_password  # Using variable, not hardcoded
  
  publicly_accessible  = false
  multi_az             = true
  
  backup_retention_period = 7
  
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  tags = {
    Environment = "Production"
  }
}''',

    # Security Group - Restricted access
    '''resource "aws_security_group" "web" {
  name        = "web-server-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from load balancer"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description = "HTTP from load balancer"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Web Server Security Group"
  }
}''',

    # S3 - Static website (intentionally public but proper)
    '''resource "aws_s3_bucket" "website" {
  bucket = "company-public-website"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  tags = {
    Purpose     = "Public Website"
    Public      = "Intentional"
    Environment = "Production"
  }
}''',

    # EC2 with proper security
    '''resource "aws_instance" "app" {
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
}'''
]

# Risky examples
risky_examples = [
    # S3 - Public customer data
    '''resource "aws_s3_bucket" "customer_data" {
  bucket = "customer-database-backup"
  acl    = "public-read"
}''',

    # S3 - Public with sensitive naming
    '''resource "aws_s3_bucket" "uploads" {
  bucket = "user-uploaded-files-prod"
  acl    = "public-read-write"
  
  # No encryption
  # No versioning
  # No logging
}''',

    # RDS - Publicly accessible database
    '''resource "aws_db_instance" "app_db" {
  identifier           = "production-database"
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  allocated_storage    = 20
  
  username             = "admin"
  password             = "MyPassword123!"  # Hardcoded password!
  
  publicly_accessible  = true  # RISKY!
  storage_encrypted    = false # RISKY!
  
  skip_final_snapshot  = true
}''',

    # Security Group - Open to world
    '''resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allow all inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to internet!
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SSH open to world!
  }
}''',

    # S3 - No security at all
    '''resource "aws_s3_bucket" "data" {
  bucket = "company-financial-records"
  # No ACL specified (defaults based on account settings)
  # No encryption
  # No versioning
  # No MFA delete
}''',

    # EC2 - Security issues
    '''resource "aws_instance" "web" {
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
}''',

    # IAM - Overly permissive
    '''resource "aws_iam_role_policy" "admin" {
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
}''',

    # Security Group - Database exposed
    '''resource "aws_security_group" "database" {
  name = "database-sg"

  ingress {
    description = "MySQL from anywhere"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Database open to internet!
  }
}'''
]

def create_dataset():
    """Create complete dataset with 100 files"""
    
    # Create directories
    os.makedirs('data/raw/safe', exist_ok=True)
    os.makedirs('data/raw/risky', exist_ok=True)
    
    # Create CSV header
    with open('data/labels.csv', 'w') as f:
        f.write('filename,category,reason,resource_type\n')
    
    print("📦 Creating dataset...\n")
    
    # Save safe examples (duplicate to reach 50)
    for i in range(50):
        example_index = i % len(safe_examples)
        content = safe_examples[example_index]
        
        filename = f"safe_{i+1:03d}.tf"
        filepath = f"data/raw/safe/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        # Extract resource type
        resource_type = content.split('"')[1] if '"' in content else 'unknown'
        
        # Log to CSV
        with open('data/labels.csv', 'a') as f:
            f.write(f'{filename},safe,"Secure configuration with encryption and proper access controls",{resource_type}\n')
        
        print(f"✅ Created {filename}")
    
    # Save risky examples (duplicate to reach 50)
    for i in range(50):
        example_index = i % len(risky_examples)
        content = risky_examples[example_index]
        
        filename = f"risky_{i+1:03d}.tf"
        filepath = f"data/raw/risky/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        resource_type = content.split('"')[1] if '"' in content else 'unknown'
        
        with open('data/labels.csv', 'a') as f:
            f.write(f'{filename},risky,"Insecure configuration with public access or missing security controls",{resource_type}\n')
        
        print(f"⚠️  Created {filename}")
    
    print(f"\n✅ Dataset created successfully!")
    print(f"   Safe examples: 50")
    print(f"   Risky examples: 50")
    print(f"   Total: 100 files")
    print(f"\n📁 Files saved in:")
    print(f"   data/raw/safe/")
    print(f"   data/raw/risky/")
    print(f"   data/labels.csv")

if __name__ == '__main__':
    create_dataset()