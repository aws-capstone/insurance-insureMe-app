terraform {
  backend "s3" {
    bucket = "tf-backend-capstone"
    key    = "capstone/project3/test-infra.tfstate"
    region = "us-east-1"
    #dynamodb_table = "your-dynamodb-table"
  }
}
