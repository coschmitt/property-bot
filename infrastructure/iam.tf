# Loader Lambda
resource "aws_iam_role" "loader_lambda_role" {
  name = "loader-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    }
  }]
}
EOF
}

resource "aws_iam_policy" "loader_lambda_policy" {
  name        = "loader-lambda-sqs-policy"
  description = "IAM policy for Loader Lambda to access SQS and dynamodb"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "${aws_dynamodb_table.listings_table.arn}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl"
      ],
      "Resource": "${aws_sqs_queue.data_queue.arn}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "loader_lambda_basic_execution" {
  role       = aws_iam_role.loader_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "loader_lambda_policy_attachment" {
  role       = aws_iam_role.loader_lambda_role.name
  policy_arn = aws_iam_policy.loader_lambda_policy.arn
}

# API lambda
resource "aws_iam_role" "property_bot_api_lambda_role" {
  name = "property-bot-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    }
  }]
}
EOF
}

resource "aws_iam_policy" "property_bot_api_lambda_policy" {
  name        = "api-lambda-dynamodb-policy"
  description = "IAM policy for API Lambda to access dynamodb"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "${aws_dynamodb_table.listings_table.arn}",
        "${aws_dynamodb_table.listings_table.arn}/index/*"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "property_bot_api_lambda_basic_execution" {
  role       = aws_iam_role.property_bot_api_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "property_bot_lambda_policy_attachment" {
  role       = aws_iam_role.property_bot_api_lambda_role.name
  policy_arn = aws_iam_policy.property_bot_api_lambda_policy.arn
}