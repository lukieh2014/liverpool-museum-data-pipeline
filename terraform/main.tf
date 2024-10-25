provider "aws" {
    region = "eu-west-2"
}

## terraform plan
## terraform apply
## terraform destroy

resource "aws_security_group" "c14-luke-workshop-sg" {
    name = "c14-luke-workshop-sg"
    description = "Security Group"
    vpc_id = "vpc-0344763624ac09cb6"

    #inbound rule
    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    #outbound rule
    egress {
        from_port = 0
        to_port = 65535
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}


#find something that already exists
data "aws_subnet" "vpc-subnet-c14"{
    filter {
        name = "tag:Name"
        values = ["c14-public-subnet-1"]
    }
}


# create a new thing (resource)
resource "aws_instance" "c14-luke-museum-ec2" {
  ami = "ami-0acc77abdfc7ed5a6"
  instance_type = "t3.nano"
  subnet_id = data.aws_subnet.vpc-subnet-c14.id

  associate_public_ip_address = true
  key_name = var.key_name

  vpc_security_group_ids = [aws_security_group.c14-luke-workshop-sg.id]

  tags = {
    Name = "c14-luke-museum-ec2"
  }
}


resource "aws_db_instance" "c14-luke-museum-db" {
    allocated_storage            = 10
    db_name                      = "postgres"
    identifier                   = "c14-luke-museum-db"
    engine                       = "postgres"
    engine_version               = "16.3"
    instance_class               = "db.t3.micro"
    publicly_accessible          = true
    performance_insights_enabled = false
    skip_final_snapshot          = true
    db_subnet_group_name         = "c14-public-subnet-group"
    vpc_security_group_ids       = [aws_security_group.c14-luke-workshop-sg.id]
    username                     = var.DB_USERNAME
    password                     = var.DB_PASSWORD
}