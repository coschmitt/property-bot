resource "random_pet" "lambda_binary_bucket_name" {
  prefix = "coschmitt"
  length = 2
}

resource "aws_s3_bucket" "property-bot-binary-bucket" {
  bucket = "property-bot-${random_pet.lambda_binary_bucket_name.id}"

  tags = local.tags
}