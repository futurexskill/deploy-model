# Docker-based AWS Lambda Deployment

This directory contains files for deploying the customer purchase prediction model as a serverless REST API using AWS Lambda with Docker containers.

## Architecture

- **Docker Container**: Packages the ML model with all dependencies (NumPy, scikit-learn)
- **AWS ECR**: Stores the Docker image
- **AWS Lambda**: Runs the containerized model (up to 10GB image size supported)
- **API Gateway**: Provides HTTP endpoint for predictions
- **EC2 (temporary)**: Used to build Docker image (terminated after build)

## Files

- `Dockerfile`: Defines the Lambda container image
- `lambda_function.py`: Lambda handler code for predictions
- `requirements.txt`: Python dependencies
- `deploy.sh`: Automated deployment script
- `test_lambda.sh`: API testing script

## Prerequisites

1. AWS CLI configured with credentials
2. EC2 key pair: `FargateDeployment.pem` in `~/.ssh/`
3. Model files: `purchase_model.pkl` and `scaler.pkl` in parent directory

## Deployment Steps

### Automated Deployment (Recommended)

```bash
cd docker-lambda
chmod +x deploy.sh test_lambda.sh
./deploy.sh
```

The script will:
1. Create ECR repository
2. Create IAM role for Lambda
3. Launch EC2 instance
4. Install Docker on EC2
5. Build Docker image on EC2
6. Push image to ECR
7. Terminate EC2 instance
8. Create Lambda function from image
9. Create API Gateway endpoint

### Testing

After deployment completes:

```bash
./test_lambda.sh
```

Or test manually:

```bash
# Single prediction
curl -X POST YOUR_API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{"age": 35, "salary": 70000}'

# Batch predictions
curl -X POST YOUR_API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{
        "customers": [
            {"age": 25, "salary": 30000},
            {"age": 40, "salary": 80000}
        ]
    }'
```

## API Specification

### Single Prediction

**Request:**
```json
{
    "age": 35,
    "salary": 70000
}
```

**Response:**
```json
{
    "age": 35,
    "salary": 70000,
    "will_purchase": true,
    "confidence": 87.5,
    "message": "Customer will likely purchase (confidence: 87.5%)"
}
```

### Batch Predictions

**Request:**
```json
{
    "customers": [
        {"age": 25, "salary": 30000},
        {"age": 40, "salary": 80000}
    ]
}
```

**Response:**
```json
{
    "predictions": [
        {
            "age": 25,
            "salary": 30000,
            "will_purchase": false,
            "confidence": 15.2
        },
        {
            "age": 40,
            "salary": 80000,
            "will_purchase": true,
            "confidence": 92.3
        }
    ],
    "count": 2
}
```

## Cost Estimation

- **Lambda**: $0.20 per 1M requests + $0.0000166667 per GB-second
- **API Gateway**: $1.00 per million requests
- **ECR**: $0.10 per GB/month for storage
- **EC2**: ~$0.01 for temporary build instance (terminated after ~5 minutes)

**Estimated monthly cost for 10,000 requests**: ~$0.02

## Cleanup

To remove all resources:

```bash
# Delete Lambda function
aws lambda delete-function --function-name customer-purchase-predictor

# Delete API Gateway
aws apigatewayv2 delete-api --api-id YOUR_API_ID

# Delete ECR repository
aws ecr delete-repository --repository-name customer-purchase-predictor --force

# Delete IAM role (detach policies first)
aws iam detach-role-policy \
    --role-name customer-purchase-predictor-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name customer-purchase-predictor-lambda-role

# Delete security group
aws ec2 delete-security-group --group-name docker-build-sg
```

## Troubleshooting

### EC2 Connection Issues

If SSH connection fails:
```bash
# Check key permissions
chmod 400 ~/.ssh/FargateDeployment.pem

# Verify security group allows SSH
aws ec2 describe-security-groups --group-names docker-build-sg
```

### Docker Build Fails

Check EC2 logs:
```bash
ssh -i ~/.ssh/FargateDeployment.pem ec2-user@YOUR_EC2_IP
sudo docker logs $(sudo docker ps -lq)
```

### Lambda Function Fails

View logs:
```bash
aws logs tail /aws/lambda/customer-purchase-predictor --follow
```

### Image Too Large

Current image size: ~800MB (well within 10GB limit)
If you need to reduce size:
- Use Alpine-based images
- Remove unnecessary dependencies
- Use multi-stage builds

## Advantages over Zip Deployment

1. **No 250MB unzipped limit**: Container images support up to 10GB
2. **Includes system libraries**: NumPy and scikit-learn work without layers
3. **Better dependency management**: Docker handles all dependencies
4. **Faster cold starts**: Models loaded once, cached in container
5. **Production-ready**: Industry standard for ML deployments

## Next Steps

1. Add CloudWatch monitoring
2. Implement request throttling
3. Add API authentication (API keys)
4. Set up custom domain name
5. Add model versioning
6. Implement A/B testing
