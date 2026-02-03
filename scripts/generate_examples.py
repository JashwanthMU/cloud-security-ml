"""
Generate example Terraform files for training
No GitHub API needed - creates synthetic examples
"""

import os

# Safe configurations (25 examples)
SAFE_EXAMPLES = [
    {
        'name': 'safe_001_encrypted_s3.tf',
        'content': '''
resource "aws_s3_bucket" "secure_data" {
  bucket = "company-secure-data"
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
  
  logging {
    target_bucket = "company-logs"
    target_prefix = "s3-access-logs/"
  }
  
  tags = {
    Environment = "production"
    Compliance  = "HIPAA"
  }
}
'''
    },
    {
        'name': 'safe_002_encrypted_rds.tf',
        'content': '''
resource "aws_db_instance" "secure_db" {
  identifier           = "secure-database"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  
  storage_encrypted    = true
  kms_key_id          = aws_kms_key.db_key.arn
  
  username             = "dbadmin"
  password             = random_password.db_password.result
  
  publicly_accessible  = false
  
  backup_retention_period = 7
  deletion_protection     = true
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
}
'''
    },
    {
        'name': 'safe_003_restricted_sg.tf',
        'content': '''
resource "aws_security_group" "web_server" {
  name        = "web_server_sg"
  description = "Allow HTTPS from internal network only"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "HTTPS from internal network"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Purpose = "Web server security"
  }
}
'''
    },
    {
        'name': 'safe_004_private_subnet.tf',
        'content': '''
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
'''
    },
    {
        'name': 'safe_005_encrypted_ebs.tf',
        'content': '''
resource "aws_ebs_volume" "secure_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  
  encrypted  = true
  kms_key_id = aws_kms_key.ebs_key.arn
  
  tags = {
    Name = "Encrypted Data Volume"
  }
}
'''
    },
]

# Risky configurations (25 examples)
RISKY_EXAMPLES = [
    {
        'name': 'risky_001_public_s3.tf',
        'content': '''
resource "aws_s3_bucket" "customer_data" {
  bucket = "prod-customer-database-backup"
  acl    = "public-read"
}
'''
    },
    {
        'name': 'risky_002_open_sg.tf',
        'content': '''
resource "aws_security_group" "allow_all" {
  name = "allow_all"
  
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
'''
    },
    {
        'name': 'risky_003_public_rds.tf',
        'content': '''
resource "aws_db_instance" "public_db" {
  identifier           = "customer-database"
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  allocated_storage    = 20
  
  username             = "admin"
  password             = "password123"
  
  publicly_accessible  = true
  skip_final_snapshot  = true
}
'''
    },
    {
        'name': 'risky_004_ssh_open.tf',
        'content': '''
resource "aws_security_group" "ssh_access" {
  name = "ssh_access"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH from anywhere"
  }
}
'''
    },
    {
        'name': 'risky_005_unencrypted_s3.tf',
        'content': '''
resource "aws_s3_bucket" "sensitive_data" {
  bucket = "financial-records-2024"
  acl    = "private"
  # No encryption!
}
'''
    },
    {
        'name': 'risky_006_hardcoded_secret.tf',
        'content': '''
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  user_data = <<-EOF
              #!/bin/bash
              export DB_PASSWORD="SuperSecret123"
              export API_KEY="1234567890abcdef"
              EOF
}
'''
    },
    {
        'name': 'risky_007_rdp_open.tf',
        'content': '''
resource "aws_security_group" "rdp_access" {
  name = "rdp_access"
  
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
'''
    },
    {
        'name': 'risky_008_no_mfa.tf',
        'content': '''
resource "aws_iam_user" "admin_user" {
  name = "admin"
  path = "/"
  
  # No MFA required!
  
  tags = {
    Role = "Administrator"
  }
}
'''
    },
]

def generate_all_examples():
    """Generate all example files"""
    
    # Create directories
    os.makedirs('data/raw/safe', exist_ok=True)
    os.makedirs('data/raw/risky', exist_ok=True)
    
    print("=" * 60)
    print("Generating Example Terraform Files")
    print("=" * 60)
    
    # Generate safe examples
    print("\nGenerating SAFE examples...")
    for example in SAFE_EXAMPLES:
        filepath = f"data/raw/safe/{example['name']}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(example['content'].strip())
        print(f"  ✅ {example['name']}")
    
    # Generate risky examples
    print("\nGenerating RISKY examples...")
    for example in RISKY_EXAMPLES:
        filepath = f"data/raw/risky/{example['name']}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(example['content'].strip())
        print(f"  ✅ {example['name']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"✅ Safe examples: {len(SAFE_EXAMPLES)}")
    print(f"✅ Risky examples: {len(RISKY_EXAMPLES)}")
    print(f"📊 Total: {len(SAFE_EXAMPLES) + len(RISKY_EXAMPLES)}")
    print("\nFiles saved in:")
    print("  - data/raw/safe/")
    print("  - data/raw/risky/")
    print("=" * 60)

if __name__ == '__main__':
    generate_all_examples()