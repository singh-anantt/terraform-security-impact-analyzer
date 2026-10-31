resource "aws_iam_policy" "create_version" {
  name = "create-version-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["iam:CreatePolicyVersion"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "create_version" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.create_version.arn
}
