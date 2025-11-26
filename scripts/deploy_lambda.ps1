
# Configuration
$AWS_REGION = "us-east-1"
$ECR_REPO_NAME = "priorizacao-backlog"
$LAMBDA_FUNC_NAME = "priorizacao-backlog-api"
$IMAGE_TAG = "latest"

# 1. Get Account ID
Write-Host "Getting AWS Account ID..."
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
if (-not $ACCOUNT_ID) {
    Write-Error "Failed to get AWS Account ID. Please run 'aws configure'."
    exit 1
}
Write-Host "Account ID: $ACCOUNT_ID"

$ECR_URI = "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
$FULL_IMAGE_URI = "$ECR_URI/$ECR_REPO_NAME`:$IMAGE_TAG"

# 2. Login to ECR
Write-Host "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# 3. Create Repository if not exists
Write-Host "Checking ECR Repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating repository $ECR_REPO_NAME..."
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION
}

# 4. Build Docker Image
Write-Host "Building Docker Image..."
# --provenance=false is required for AWS Lambda compatibility with newer Docker versions
# --platform linux/amd64 ensures compatibility with Lambda x86_64 architecture
docker build --provenance=false --platform linux/amd64 -f Dockerfile.lambda -t $ECR_REPO_NAME .

# 5. Tag and Push
Write-Host "Pushing Image to ECR..."
docker tag $ECR_REPO_NAME`:$IMAGE_TAG $FULL_IMAGE_URI
docker push $FULL_IMAGE_URI

# 6. Create or Update Lambda
Write-Host "Updating Lambda Function..."
aws lambda get-function --function-name $LAMBDA_FUNC_NAME --region $AWS_REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Function exists. Updating code..."
    aws lambda update-function-code --function-name $LAMBDA_FUNC_NAME --image-uri $FULL_IMAGE_URI --region $AWS_REGION
    
    Write-Host "Updating configuration (Timeout=300s, Memory=1024MB, ModelID, Guardrails)..."
    aws lambda update-function-configuration --function-name $LAMBDA_FUNC_NAME --timeout 300 --memory-size 1024 --environment "Variables={BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0,BEDROCK_GUARDRAIL_ID=fwfavybfrb90,BEDROCK_GUARDRAIL_VERSION=DRAFT,DATABASE_TYPE=dynamodb,DYNAMODB_TABLE_SETTINGS=backlog_settings,DYNAMODB_TABLE_CONVERSATIONS=backlog_conversations,LLM_PROVIDER=bedrock,DYNAMODB_TABLE_ITEMS=backlog_items,RESULTADO_SHEET_NAME=Roadmap}" --region $AWS_REGION

    # Wait for update
    Write-Host "Waiting for update to complete..."
    aws lambda wait function-updated --function-name $LAMBDA_FUNC_NAME --region $AWS_REGION
}
else {
    Write-Host "Function does not exist. Creating..."
    # Note: You need a role ARN here. For now, we'll ask the user or fail if not provided.
    # We will try to create a basic role or ask user to provide one.
    # For simplicity in this script, we assume the user might need to create it manually first or we use a known role.
    # Let's try to find a role or create one? Creating IAM roles via CLI is complex due to trust policies.
    
    Write-Warning "Lambda function '$LAMBDA_FUNC_NAME' does not exist."
    Write-Warning "Please create the function manually in AWS Console using the Container Image URI: $FULL_IMAGE_URI"
    Write-Warning "Or provide an IAM Role ARN to create it via CLI."
}

Write-Host "Deployment process finished!"
Write-Host "Image URI: $FULL_IMAGE_URI"
