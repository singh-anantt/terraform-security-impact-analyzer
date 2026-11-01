resource "aws_iam_policy" "policy_a" {
  name = "policy-a"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_policy" "policy_b" {
  name = "policy-b"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_a" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.policy_a.arn
}

resource "aws_iam_role_policy_attachment" "attach_b" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.policy_b.arn
}
