
output "rds_instance_address" {
  description = "Public IP address of the RDS instance"
  value       = aws_db_instance.c14-luke-museum-db.endpoint
}

output "ec2_instance_address" {
  description = "Public IP address of the EC2 instance"
  value = aws_instance.c14-luke-museum-ec2.public_ip
}