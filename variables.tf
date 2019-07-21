variable "slack_url" {
  type        = "string"
  description = "Slack URL"
}

variable "region" {
  default = "ap-northeast-1"
}

variable "bucket" {
  default = "<bucket-for-terraform>"
}
