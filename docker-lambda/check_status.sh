#!/bin/bash

echo "Checking AWS Lambda Deployment Status..."
echo "========================================"
echo ""

# Check ECR repository and images
echo "ECR Repository:"
aws ecr describe-repositories --repository-names customer-purchase-predictor --region us-east-1 --query 'repositories[0].[repositoryName,repositoryUri]' --output text 2>/dev/null || echo "Not found"

echo ""
echo "ECR Images:"
aws ecr describe-images --repository-name customer-purchase-predictor --region us-east-1 --query 'imageDetails[*].[imageTags[0],imagePushedAt,imageSizeInBytes]' --output table 2>/dev/null || echo "No images yet"

echo ""
echo "EC2 Instances (docker-build-temp):"
aws ec2 describe-instances --filters "Name=tag:Name,Values=docker-build-temp" --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' --output table

echo ""
echo "Lambda Function:"
aws lambda get-function --function-name customer-purchase-predictor --region us-east-1 --query 'Configuration.[FunctionName,State,LastUpdateStatus]' --output table 2>/dev/null || echo "Not created yet"

echo ""
echo "API Gateway:"
aws apigatewayv2 get-apis --query 'Items[?Name==`customer-purchase-api`].[Name,ApiEndpoint]' --output table 2>/dev/null || echo "Not created yet"

echo ""
echo "========================================"
