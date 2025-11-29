#!/bin/bash

set -e

# Configuration
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="customer-purchase-predictor"
LAMBDA_FUNCTION_NAME="customer-purchase-predictor"
EC2_KEY_NAME="FargateDeployment"
EC2_KEY_PATH="$HOME/.ssh/FargateDeployment-new.pem"
INSTANCE_TYPE="t2.micro"
AMI_ID="ami-0fa3fe0fa7920f68e"  # Amazon Linux 2023 in us-east-1

echo "======================================"
echo "Rebuilding Docker Image on EC2"
echo "======================================"
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo ""

# Get security group
SG_NAME="docker-build-sg"
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")

if [ "$SG_ID" = "None" ]; then
    echo "Error: Security group not found. Run deploy.sh first."
    exit 1
fi

# Launch EC2 instance
echo "Step 1: Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $EC2_KEY_NAME \
    --security-group-ids $SG_ID \
    --instance-initiated-shutdown-behavior terminate \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=docker-rebuild-temp}]' \
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

# Step 2: Build Docker image on EC2
echo "Step 2: Building Docker image on EC2..."

# Create build script
cat > /tmp/rebuild-docker.sh << 'BUILDSCRIPT'
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

chmod +x /tmp/rebuild-docker.sh

# Copy files to EC2
echo "Copying files to EC2 instance..."
scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    Dockerfile requirements.txt lambda_function.py \
    ../purchase_model.pkl ../scaler.pkl \
    ec2-user@$PUBLIC_IP:/tmp/

scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    /tmp/rebuild-docker.sh ec2-user@$PUBLIC_IP:/tmp/

# Execute build on EC2
echo "Executing Docker build on EC2..."
ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    ec2-user@$PUBLIC_IP << 'ENDSSH'
mkdir -p /home/ec2-user/docker-lambda
mv /tmp/Dockerfile /tmp/requirements.txt /tmp/lambda_function.py /tmp/purchase_model.pkl /tmp/scaler.pkl /home/ec2-user/docker-lambda/
cd /home/ec2-user
chmod +x /tmp/rebuild-docker.sh
/tmp/rebuild-docker.sh
ENDSSH

echo ""

# Step 3: Push to ECR
echo "Step 3: Pushing image to ECR..."

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"

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

# Step 4: Terminate EC2 instance
echo "Step 4: Terminating EC2 instance..."
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
echo "EC2 instance termination initiated"
echo ""

# Step 5: Update Lambda function
echo "Step 5: Updating Lambda function with new image..."

# Wait for ECR image to be available
echo "Waiting for ECR image to be available..."
sleep 10

# Update Lambda function code
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --image-uri ${ECR_URI}:latest \
    --region $REGION

echo "Waiting for Lambda function to be updated..."
aws lambda wait function-updated --function-name $LAMBDA_FUNCTION_NAME --region $REGION

echo ""
echo "======================================"
echo "Update Complete!"
echo "======================================"
echo "Lambda function updated with new Docker image"
echo ""

# Get API endpoint
API_ENDPOINT=$(cat api_endpoint.txt 2>/dev/null || echo "")
if [ -n "$API_ENDPOINT" ]; then
    echo "Test with:"
    echo "curl -X POST $API_ENDPOINT -H 'Content-Type: application/json' -d '{\"age\": 35, \"salary\": 50000}'"
fi
