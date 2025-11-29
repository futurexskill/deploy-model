#!/bin/bash

set -e

# Configuration
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="customer-purchase-predictor"
LAMBDA_FUNCTION_NAME="customer-purchase-predictor"
LAMBDA_ROLE_NAME="customer-purchase-predictor-lambda-role"
API_NAME="customer-purchase-api"
EC2_KEY_NAME="FargateDeployment"
EC2_KEY_PATH="$HOME/.ssh/FargateDeployment-new.pem"
INSTANCE_TYPE="t2.micro"
AMI_ID="ami-0fa3fe0fa7920f68e"  # Amazon Linux 2023 in us-east-1

echo "======================================"
echo "AWS Lambda Docker Deployment"
echo "======================================"
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo "ECR Repo: $ECR_REPO_NAME"
echo "Lambda Function: $LAMBDA_FUNCTION_NAME"
echo ""

# Step 1: Create ECR Repository
echo "Step 1: Creating ECR repository..."
if aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $REGION 2>/dev/null; then
    echo "ECR repository already exists"
else
    aws ecr create-repository \
        --repository-name $ECR_REPO_NAME \
        --region $REGION
    echo "ECR repository created"
fi

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"
echo "ECR URI: $ECR_URI"
echo ""

# Step 2: Create IAM Role for Lambda
echo "Step 2: Creating IAM role for Lambda..."
if aws iam get-role --role-name $LAMBDA_ROLE_NAME 2>/dev/null; then
    echo "IAM role already exists"
else
    cat > /tmp/lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role \
        --role-name $LAMBDA_ROLE_NAME \
        --assume-role-policy-document file:///tmp/lambda-trust-policy.json
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $LAMBDA_ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    echo "IAM role created"
    echo "Waiting 10 seconds for IAM role to propagate..."
    sleep 10
fi

LAMBDA_ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query 'Role.Arn' --output text)
echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"
echo ""

# Step 3: Launch EC2 instance
echo "Step 3: Launching EC2 instance for Docker build..."

# Check if key pair permissions are correct
if [ ! -f "$EC2_KEY_PATH" ]; then
    echo "Error: EC2 key not found at $EC2_KEY_PATH"
    exit 1
fi

chmod 400 "$EC2_KEY_PATH"

# Create security group
SG_NAME="docker-build-sg"
echo "Creating security group..."
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")

if [ "$SG_ID" = "None" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for Docker build instance" \
        --query 'GroupId' \
        --output text)
    
    # Add SSH rule
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    echo "Security group created: $SG_ID"
else
    echo "Security group already exists: $SG_ID"
fi

# Launch EC2 instance
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $EC2_KEY_NAME \
    --security-group-ids $SG_ID \
    --instance-initiated-shutdown-behavior terminate \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=docker-build-temp}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Instance is running at: $PUBLIC_IP"
echo "Waiting 30 seconds for SSH to be ready..."
sleep 30
echo ""

# Step 4: Copy files to EC2 and build Docker image
echo "Step 4: Building Docker image on EC2..."

# Create a build script
cat > /tmp/build-docker.sh << 'BUILDSCRIPT'
#!/bin/bash
set -e

# Install Docker
echo "Installing Docker..."
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install AWS CLI v2
echo "Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Build Docker image
cd /home/ec2-user/docker-lambda
echo "Building Docker image..."
sudo docker build -t customer-purchase-predictor .

echo "Build complete!"
BUILDSCRIPT

chmod +x /tmp/build-docker.sh

# Copy files to EC2
echo "Copying files to EC2 instance..."
scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    Dockerfile requirements.txt lambda_function.py \
    ../purchase_model.pkl ../scaler.pkl \
    ec2-user@$PUBLIC_IP:/tmp/

scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    /tmp/build-docker.sh ec2-user@$PUBLIC_IP:/tmp/

# Execute build on EC2
echo "Executing Docker build on EC2..."
ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    ec2-user@$PUBLIC_IP << 'ENDSSH'
mkdir -p /home/ec2-user/docker-lambda
mv /tmp/Dockerfile /tmp/requirements.txt /tmp/lambda_function.py /tmp/purchase_model.pkl /tmp/scaler.pkl /home/ec2-user/docker-lambda/
cd /home/ec2-user
chmod +x /tmp/build-docker.sh
/tmp/build-docker.sh
ENDSSH

echo ""

# Step 5: Tag and push to ECR
echo "Step 5: Tagging and pushing image to ECR..."

# Copy AWS credentials to EC2 (temporary)
echo "Configuring AWS credentials on EC2..."
ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    ec2-user@$PUBLIC_IP << ENDSSH
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
export AWS_DEFAULT_REGION=$REGION

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | sudo docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Tag and push
echo "Tagging image..."
sudo docker tag customer-purchase-predictor:latest ${ECR_URI}:latest

echo "Pushing image to ECR..."
sudo docker push ${ECR_URI}:latest

echo "Image pushed successfully!"
ENDSSH

echo ""

# Step 6: Terminate EC2 instance
echo "Step 6: Terminating EC2 instance..."
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
echo "EC2 instance termination initiated"
echo ""

# Step 7: Create Lambda function from container image
echo "Step 7: Creating Lambda function from container image..."

# Wait a bit for ECR image to be available
echo "Waiting for ECR image to be available..."
sleep 10

# Delete existing function if it exists
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Deleting existing Lambda function..."
    aws lambda delete-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION
    sleep 5
fi

# Create Lambda function
aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --package-type Image \
    --code ImageUri=${ECR_URI}:latest \
    --role $LAMBDA_ROLE_ARN \
    --timeout 30 \
    --memory-size 512 \
    --region $REGION

echo "Lambda function created successfully!"
echo ""

# Step 8: Create API Gateway
echo "Step 8: Creating API Gateway..."

# Create HTTP API
API_ID=$(aws apigatewayv2 create-api \
    --name $API_NAME \
    --protocol-type HTTP \
    --target arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME} \
    --region $REGION \
    --query 'ApiId' \
    --output text)

echo "API Gateway created: $API_ID"

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*" \
    --region $REGION

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api --api-id $API_ID --region $REGION --query 'ApiEndpoint' --output text)

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "Lambda Function: $LAMBDA_FUNCTION_NAME"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Test with:"
echo "curl -X POST $API_ENDPOINT -H 'Content-Type: application/json' -d '{\"age\": 35, \"salary\": 50000}'"
echo ""
echo "Save this endpoint for future use:"
echo "$API_ENDPOINT" > api_endpoint.txt
echo "Endpoint saved to api_endpoint.txt"
