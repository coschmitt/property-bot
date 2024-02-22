
data "archive_file" "loader_zip" {
  type        = "zip"
  source_file = "${path.module}/../loader/load.py"
  output_path = "${path.module}/.loader.zip"
}

resource "aws_lambda_function" "property_bot_loader_lambda" {
  function_name    = "property-bot-loader"
  s3_bucket        = aws_s3_bucket.property-bot-binary-bucket.id
  s3_key           = aws_s3_object.loader_upload.key
  runtime          = "python3.9"
  handler          = "load.load_from_sqs"
  role             = aws_iam_role.loader_lambda_role.arn
  timeout          = 30
  source_code_hash = data.archive_file.loader_zip.output_base64sha256

  tags = local.tags
}

resource "aws_lambda_event_source_mapping" "loader" {
  event_source_arn = aws_sqs_queue.data_queue.arn
  function_name = aws_lambda_function.property_bot_loader_lambda.function_name
  batch_size = 10
}

resource "aws_s3_object" "loader_upload" {
  bucket = aws_s3_bucket.property-bot-binary-bucket.id
  key    = "loader.zip"
  source = data.archive_file.loader_zip.output_path
  etag   = data.archive_file.loader_zip.output_base64sha256
}