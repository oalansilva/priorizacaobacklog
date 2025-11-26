
# Configuration
$AWS_REGION = "us-east-1"
$ROLE_NAME = "priorizacao-backlog-lambda-role"
$LAMBDA_FUNC_NAME = "priorizacao-backlog-api"
$ECR_REPO_NAME = "priorizacao-backlog"
$IMAGE_TAG = "latest"

# 1. Get Account ID
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$IMAGE_URI = "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME`:$IMAGE_TAG"

# 2. Create IAM Role
Write-Host "Checking IAM Role '$ROLE_NAME'..."
aws iam get-role --role-name $ROLE_NAME 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating IAM Role..."
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://lambda-trust-policy.json
    
    Write-Host "Attaching Policies..."
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
    
    Write-Host "Waiting for role propagation (10s)..."
    Start-Sleep -Seconds 10
}
else {
    Write-Host "Role already exists."
}

$ROLE_ARN = "arn:aws:iam::$ACCOUNT_ID`:role/$ROLE_NAME"

# 3. Create Lambda Function
Write-Host "Creating/Updating Lambda Function..."
aws lambda get-function --function-name $LAMBDA_FUNC_NAME --region $AWS_REGION 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Function..."
    aws lambda create-function `
        --function-name $LAMBDA_FUNC_NAME `
        --package-type Image `
        --code ImageUri=$IMAGE_URI `
        --role $ROLE_ARN `
        --timeout 300 `
        --memory-size 1024 `
        --region $AWS_REGION
}
else {
    Write-Host "Function exists. Updating configuration..."
    aws lambda update-function-configuration `
        --function-name $LAMBDA_FUNC_NAME `
        --timeout 300 `
        --memory-size 1024 `
        --role $ROLE_ARN `
        --region $AWS_REGION
        
    aws lambda update-function-code `
        --function-name $LAMBDA_FUNC_NAME `
        --image-uri $IMAGE_URI `
        --region $AWS_REGION
}

Write-Host "Lambda setup complete!"
