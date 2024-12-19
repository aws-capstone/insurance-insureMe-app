resource "tls_private_key" "mykey" {
  algorithm = "RSA"
}

resource "aws_key_pair" "aws_key" {
  key_name   = "insureme-test-key"
  public_key = tls_private_key.mykey.public_key_openssh

}

resource "null_resource" "update_permissions" {
  provisioner "local-exec" {
    command = <<EOT
      echo '${tls_private_key.mykey.private_key_openssh}' > ./insureme-test-ec2.pem
      chmod 400 ./insureme-test-ec2.pem
    EOT
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}


resource "aws_ssm_parameter" "ec2_private_key" {
  name        = "/capstone/project3/insureme-test-ec2_private_key"
  description = "Private key of ec2 instance"
  type        = "SecureString"
  value       = tls_private_key.mykey.private_key_openssh
}

resource "aws_ssm_parameter" "ec2_public_key" {
  name        = "/capstone/project1/insureme-test-ec2_public_key"
  description = "Public key of ec2 instance"
  type        = "SecureString"
  value       = tls_private_key.mykey.public_key_openssh
}


resource "aws_instance" "myec2" {
  ami           = var.amiid
  instance_type = "t2.micro"
  key_name = aws_key_pair.aws_key.key_name
  subnet_id = aws_subnet.subnet-1.id
  vpc_security_group_ids = [aws_security_group.sa-sg.id]
  tags = {
    Name = "insureme-test-ec2"
  }
}