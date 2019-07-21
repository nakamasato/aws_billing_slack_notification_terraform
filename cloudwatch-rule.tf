resource "aws_cloudwatch_event_rule" "billing-notification-rule" {
  name                = "billing-notification-rule"
  description         = "billing-notification-rule"
  schedule_expression = "cron(0 1 * * ? *)"
}

resource "aws_cloudwatch_event_target" "billing-notification-event-target" {
  rule      = "${aws_cloudwatch_event_rule.billing-notification-rule.name}"
  target_id = "billing-notification"
  arn       = "${aws_lambda_function.billing-notification.arn}"
}

resource "aws_lambda_permission" "allow-cloudwatch-to-call-billing-notification" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.billing-notification.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.billing-notification-rule.arn}"
}
