resource "null_resource" "api_dependencies" {
  provisioner "local-exec" {
    command = "cd ${path.module}/../api && ./gradlew build"
  }

  triggers = {
    api  = sha256(file("${path.module}/../api/src/main/java/api/PropertyAPI.java"))
  }
}

resource "aws_lambda_function" "api" {
  function_name    = "property-bot-api"
  filename      = "${path.module}/../api/build/distributions/api-1.0-SNAPSHOT.zip"
  source_code_hash = "${filebase64sha256("${path.module}/../api/build/distributions/api-1.0-SNAPSHOT.zip")}"
  runtime          = "java11"
  handler          = "api.PropertyAPI"
  role             = aws_iam_role.property_bot_api_lambda_role.arn
  memory_size      = 128
  timeout          = 30
  tags = local.tags

  depends_on = [
    resource.null_resource.api_dependencies
  ]
}

# API Gateway

resource "aws_api_gateway_rest_api" "property-bot" {
  name        = "property-bot-gateway"
  description = "Property Bot API Gateway"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.property-bot.id}"
  parent_id   = "${aws_api_gateway_rest_api.property-bot.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.property-bot.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.property-bot.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.api.invoke_arn}"
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = "${aws_api_gateway_rest_api.property-bot.id}"
  resource_id   = "${aws_api_gateway_rest_api.property-bot.root_resource_id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = "${aws_api_gateway_rest_api.property-bot.id}"
  resource_id = "${aws_api_gateway_method.proxy_root.resource_id}"
  http_method = "${aws_api_gateway_method.proxy_root.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.api.invoke_arn}"
}

resource "aws_api_gateway_deployment" "property-bot" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = "${aws_api_gateway_rest_api.property-bot.id}"
  stage_name  = "prod"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:invokefunction"
  function_name = "${aws_lambda_function.api.function_name}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.property-bot.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw2" {
  statement_id  = "AllowAPIGatewayInvokeMore"
  action        = "lambda:invokefunction"
  function_name = "${aws_lambda_function.api.function_name}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.property-bot.execution_arn}/*/*/*"
}

