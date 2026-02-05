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