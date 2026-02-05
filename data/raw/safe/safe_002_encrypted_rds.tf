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