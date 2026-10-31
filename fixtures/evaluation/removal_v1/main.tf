resource "aws_iam_policy" "example" {
  name = "removal-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "*"
    }]
  })
}
