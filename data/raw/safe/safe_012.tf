resource "aws_db_instance" "main" {
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
}