resource "aws_dynamodb_table" "listings_table" {
  name           = "redfin-listings-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "zipcode"
  range_key      = "address"

  attribute {
    name = "address"
    type = "S"
  }

  attribute{
    name = "zipcode"
    type = "S"
  }

  tags = local.tags
}