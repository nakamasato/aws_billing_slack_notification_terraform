terraform {
  required_version = ">= 0.11.0"

  backend "s3" {
    bucket                  = "<bucket-for-terraform>"
    key                     = "terraform-lambda.tfstate"
    region                  = "ap-northeast-1"
    shared_credentials_file = "~/.aws/credentials"
    profile                 = "default"
  }
}
