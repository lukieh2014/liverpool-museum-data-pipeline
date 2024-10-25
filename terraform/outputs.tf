
output "rds_instance_address" {
  description = "Public IP address of the RDS instance"
  value       = aws_db_instance.c14-luke-museum-db.endpoint
}
