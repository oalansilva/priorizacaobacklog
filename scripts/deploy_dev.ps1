
# Configuration
$AWS_REGION = "us-east-1"
$ECR_REPO_NAME = "priorizacao-backlog-dev"
$LAMBDA_FUNC_NAME = "priorizacao-backlog-dev"
$IMAGE_TAG = "latest"

# 1. Get Account ID
Write-Host "Getting AWS Account ID..."
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
if (-not $ACCOUNT_ID) {
    Write-Error "Failed to get AWS Account ID. Please run 'aws configure'."
    exit 1
}
Write-Host "Account ID: $ACCOUNT_ID"

# CHECK FOR DOCKER (Support for Rancher Desktop)
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker command not found in PATH. Checking Rancher Desktop..."
    
    $RancherDockerPath = "C:\Program Files\Rancher Desktop\resources\resources\win32\bin"
    if (Test-Path "$RancherDockerPath\docker.exe") {
        Write-Host "Found Docker in Rancher Desktop path. Adding to session PATH."
        $env:PATH = "$RancherDockerPath;$env:PATH"
        
        # Switch to default context
        Write-Host "Switching Docker context to 'default'..."
        try {
            & docker context use default
        }
        catch {
            Write-Warning "Failed to switch context to default."
        }
    }
    else {
        Write-Error "Docker not found! Please install Docker Desktop or Rancher Desktop."
        exit 1
    }
}

$ECR_URI = "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
$FULL_IMAGE_URI = "$ECR_URI/$ECR_REPO_NAME`:$IMAGE_TAG"

# 2. Login to ECR
Write-Host "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | & docker login --username AWS --password-stdin $ECR_URI

# 3. Create Repository if not exists
Write-Host "Checking ECR Repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating repository $ECR_REPO_NAME..."
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION
}

# 4. Build Docker Image
Write-Host "Building Docker Image..."

# Generate Version (Timestamp)
$VERSION_DATE = Get-Date -Format "yyyyMMdd.HHmm"
Write-Host "Injecting Version: $VERSION_DATE-DEV"
Set-Content -Path "app/version.txt" -Value "$VERSION_DATE-DEV"

# Build
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
    
    Write-Host "Updating configuration for DEV..."
    # Configurando tabelas _dev para isolamento
    aws lambda update-function-configuration --function-name $LAMBDA_FUNC_NAME --timeout 300 --memory-size 1024 --environment "Variables={BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0,DATABASE_TYPE=dynamodb,DYNAMODB_TABLE_SETTINGS=backlog_settings_dev,DYNAMODB_TABLE_CONVERSATIONS=backlog_conversations_dev,LLM_PROVIDER=bedrock,DYNAMODB_TABLE_ITEMS=backlog_items_dev,DYNAMODB_TABLE_ROADMAPS=backlog_roadmaps_dev,DYNAMODB_TABLE_USERS=backlog_users_dev,RESULTADO_SHEET_NAME=Roadmap}" --region $AWS_REGION

    Write-Host "Waiting for update to complete..."
    aws lambda wait function-updated --function-name $LAMBDA_FUNC_NAME --region $AWS_REGION
}
else {
    Write-Host "Function does not exist. Creating..."
    Write-Warning "Lambda function '$LAMBDA_FUNC_NAME' does not exist."
    Write-Warning "Please create the function manually in AWS Console (or via CLI if you have Role ARN) using URI: $FULL_IMAGE_URI"
}

Write-Host "Success! DEV Environment Deployed."
