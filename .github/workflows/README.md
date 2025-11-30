# GitHub Actions ML CI/CD Pipeline

This directory contains the GitHub Actions workflow for automating ML model training, testing, and deployment.

## Workflow Overview

The CI/CD pipeline consists of 3 main jobs that run sequentially:

### 1. Train Model (`train-model`)
- Sets up Python environment
- Installs dependencies
- Trains the ML model using `train_model.py`
- Uploads trained model artifacts (pkl files)

### 2. Test Model (`test-model`)
- Downloads trained model artifacts
- Runs comprehensive validation tests
- Checks model performance metrics
- Generates test report
- Blocks deployment if tests fail

### 3. Deploy to AWS (`deploy-to-aws`)
- Only runs if all tests pass
- Uploads models to S3
- Builds Docker image with new model
- Pushes image to Amazon ECR
- Updates Lambda function
- Tests deployed Lambda function
- Creates deployment tag

## Workflow Triggers

The workflow runs automatically when:
- Python files (`*.py`) are pushed to main branch
- CSV data files (`*.csv`) are changed
- `requirements.txt` is updated
- Workflow file itself is modified

You can also trigger it manually from GitHub Actions UI.

## Setup Instructions

### 1. Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:
```
AWS_ACCESS_KEY_ID: Your AWS access key
AWS_SECRET_ACCESS_KEY: Your AWS secret key
```

### 2. Verify AWS Resources

Ensure these exist in your AWS account:
- S3 bucket: `customer-purchase-predictor-models`
- ECR repository: `customer-purchase-predictor`
- Lambda function: `customer-purchase-predictor`
- IAM user with permissions for S3, ECR, and Lambda

### 3. Test Workflow Locally (Optional)

Install Act to test GitHub Actions locally:
```bash
brew install act  # macOS
act -l            # List workflows
act push          # Run workflow
```

## Workflow File Location

```
.github/workflows/ml-pipeline.yml
```

## Test Files

The validation tests are in:
```
tests/test_model.py
```

## Monitoring Workflow

### View Workflow Runs
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "ML Model CI/CD Pipeline"
4. View individual run details

### Check Logs
- Each job has detailed logs
- Click on any step to see its output
- Download artifacts (models, reports) from run page

## Workflow Status Badge

Add this to your README.md:
```markdown
![ML Pipeline](https://github.com/futurexskill/deploy-model/actions/workflows/ml-pipeline.yml/badge.svg)
```

## Understanding the Pipeline Flow

```
┌─────────────────────┐
│   Code Push         │
│   (Python/CSV)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Job 1: Train       │
│  - Install deps     │
│  - Train model      │
│  - Upload artifacts │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Job 2: Test        │
│  - Download model   │
│  - Run tests        │
│  - Validate metrics │
└──────────┬──────────┘
           │
           ▼ (only if tests pass)
┌─────────────────────┐
│  Job 3: Deploy      │
│  - Upload to S3     │
│  - Build Docker     │
│  - Update Lambda    │
│  - Test deployment  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ✅ Success!       │
│   Model Deployed    │
└─────────────────────┘
```

## What Gets Tested

1. **Model Files**: Checks if pkl files exist
2. **Model Loading**: Verifies model can be loaded
3. **Model Type**: Confirms it's RandomForestClassifier
4. **Model Attributes**: Validates methods and features
5. **Scaler Attributes**: Checks StandardScaler setup
6. **Predictions**: Tests with known inputs
7. **Performance**: Measures accuracy (minimum 75%)
8. **Consistency**: Ensures reproducible predictions

## Deployment Steps

When tests pass:
1. Models uploaded to S3
2. Docker image built with new models
3. Image tagged with commit SHA and 'latest'
4. Image pushed to ECR
5. Lambda function updated with new image
6. Lambda function tested with sample request
7. Git tag created for deployment tracking

## Rollback Process

If deployment fails or issues arise:

```bash
# List deployment tags
git tag -l "deployment-*"

# Find the last successful deployment
PREVIOUS_TAG="deployment-20251129-120000"

# Get the commit SHA from that tag
PREVIOUS_SHA=$(git rev-list -n 1 $PREVIOUS_TAG)

# Update Lambda to previous image
aws lambda update-function-code \
  --function-name customer-purchase-predictor \
  --image-uri 295470186437.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-predictor:$PREVIOUS_SHA
```

## Cost Considerations

- **GitHub Actions**: 2,000 free minutes/month
- **This workflow**: ~5-10 minutes per run
- **ECR Storage**: $0.10/GB/month
- **Lambda**: Free tier covers most usage

## Best Practices

1. ✅ Always run tests before deploying
2. ✅ Use meaningful commit messages
3. ✅ Review workflow logs after each run
4. ✅ Keep secrets secure in GitHub Secrets
5. ✅ Monitor AWS costs regularly
6. ✅ Tag successful deployments
7. ✅ Document any workflow changes

## Troubleshooting

### Workflow Fails at Training
- Check if `train_model.py` works locally
- Verify dataset file exists
- Check dependency versions

### Tests Fail
- Review test output in Actions logs
- Run tests locally: `python tests/test_model.py`
- Check model performance metrics

### Deployment Fails
- Verify AWS credentials in secrets
- Check AWS resource names match workflow
- Ensure IAM permissions are correct
- Verify ECR repository exists

### Docker Build Fails
- Check Dockerfile syntax
- Verify all required files are in docker-lambda/
- Ensure model files are copied correctly

## Manual Deployment

If you need to deploy manually:

```bash
# Train model
python train_model.py

# Run tests
python tests/test_model.py

# Deploy (from docker-lambda directory)
cd docker-lambda
./update_lambda.sh
```

## Next Steps

1. Add notifications (Slack, email) for deployment status
2. Implement blue-green deployments
3. Add model performance monitoring
4. Set up automatic rollback on errors
5. Add integration tests for API endpoints
6. Implement model versioning in S3
