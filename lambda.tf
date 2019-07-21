resource "aws_lambda_function" "billing-notification" {
  function_name = "billing-notification"

  # The bucket name as created earlier with "aws s3api create-bucket"
  s3_bucket = "${var.bucket}"
  s3_key    = "billing-notification/function.zip"

  handler = "app.lambda_handler"
  runtime = "python3.6"

  role = "${aws_iam_role.lambda-billing-notification-role.arn}"

  environment {
    variables = {
      SLACK_WEBHOOK_URL = "${var.slack_url}"
    }
  }
}

resource "aws_iam_role" "lambda-billing-notification-role" {
  name = "lambda-billing-notification-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda-billing-notification-policy" {
  name        = "lambda-billing-notification-policy"
  description = "lambda billing notification policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ce:GetCostAndUsage"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda-billing-notification-poliy-attach" {
  role       = "${aws_iam_role.lambda-billing-notification-role.name}"
  policy_arn = "${aws_iam_policy.lambda-billing-notification-policy.arn}"
}
