resource "aws_db_instance" "app_db" {
  identifier           = "production-database"
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  allocated_storage    = 20
  
  username             = "admin"
  password             = "MyPassword123!"  # Hardcoded password!
  
  publicly_accessible  = true  # RISKY!
  storage_encrypted    = false # RISKY!
  
  skip_final_snapshot  = true
}