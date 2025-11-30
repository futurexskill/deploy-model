# Setting Up GitHub Actions CI/CD Pipeline

Follow these steps to enable automated ML model deployment with GitHub Actions.

## Step 1: Add AWS Credentials to GitHub Secrets

1. Go to your GitHub repository: https://github.com/futurexskill/deploy-model
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

### Secret 1: AWS_ACCESS_KEY_ID
- Name: `AWS_ACCESS_KEY_ID`
- Value: Your AWS access key ID (get from AWS IAM console)

### Secret 2: AWS_SECRET_ACCESS_KEY
- Name: `AWS_SECRET_ACCESS_KEY`
- Value: Your AWS secret access key (get from AWS IAM console)

**Finding Your AWS Credentials:**
```bash
# Show your current AWS credentials
cat ~/.aws/credentials

# Or get from AWS CLI config
aws configure get aws_access_key_id
aws configure get aws_secret_access_key
```

## Step 2: Verify AWS Resources Exist

Make sure these resources are set up in your AWS account (us-east-1):

```bash
# Check S3 bucket
aws s3 ls s3://customer-purchase-predictor-models

# Check ECR repository
aws ecr describe-repositories --repository-names customer-purchase-predictor

# Check Lambda function
aws lambda get-function --function-name customer-purchase-predictor
```

All these should already exist from your previous deployment.

## Step 3: Test the Workflow Locally (Optional)

Before pushing to GitHub, test that everything works:

```bash
# Run model validation tests
python tests/test_model.py

# Should see:
# ✅ ALL TESTS PASSED!
# 🚀 Model is ready for deployment!
```

## Step 4: Commit and Push Workflow Files

```bash
# Add all workflow files
git add .github/ tests/

# Commit
git commit -m "Add GitHub Actions CI/CD pipeline for ML model deployment"

# Push to trigger workflow
git push origin main
```

## Step 5: Monitor the Workflow

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You'll see "ML Model CI/CD Pipeline" running
4. Click on the workflow run to see details
5. Watch the progress of each job:
   - ✅ Train Model
   - ✅ Test Model  
   - ✅ Deploy to AWS

The entire process takes about 5-10 minutes.

## Step 6: Verify Deployment

After the workflow completes successfully:

```bash
# Test the deployed Lambda function
curl -X POST https://2y2wvahuza.execute-api.us-east-1.amazonaws.com \
  -H 'Content-Type: application/json' \
  -d '{"age": 35, "salary": 70000}'

# Should return:
# {"age": 35, "salary": 70000, "will_purchase": true, "confidence": 100.0, ...}
```

## How the Pipeline Works

### Automatic Triggers
The workflow runs automatically when you push changes to:
- Any Python file (`*.py`)
- Any CSV data file (`*.csv`)
- `requirements.txt`
- The workflow file itself

### Manual Trigger
You can also trigger it manually:
1. Go to **Actions** tab
2. Select "ML Model CI/CD Pipeline"
3. Click **Run workflow** → **Run workflow**

### Pipeline Flow

```
Push Code → Train Model → Run Tests → Deploy to AWS
              ↓              ↓             ↓
           Upload PKL    Validate     Update Lambda
           Artifacts    Performance   Test Endpoint
```

## Workflow Jobs Explained

### Job 1: Train Model
```yaml
- Checkout code
- Setup Python 3.11
- Install dependencies
- Run train_model.py
- Upload model artifacts
```

### Job 2: Test Model
```yaml
- Download model artifacts
- Run validation tests:
  ✓ Model files exist
  ✓ Model loads correctly
  ✓ Predictions are valid
  ✓ Accuracy >= 75%
  ✓ Results are consistent
- Generate test report
```

### Job 3: Deploy to AWS (Only if tests pass)
```yaml
- Upload models to S3
- Build Docker image
- Push to Amazon ECR
- Update Lambda function
- Test deployed function
- Create deployment tag
```

## Testing Your Changes

### Make a Small Change
```bash
# Edit train_model.py (e.g., change a comment)
echo "# Updated model" >> train_model.py

# Commit and push
git add train_model.py
git commit -m "Test CI/CD pipeline"
git push origin main
```

### Watch It Deploy
1. Go to **Actions** tab on GitHub
2. See your workflow running
3. After ~5-10 minutes, it should complete
4. Test the updated Lambda function

## Common Issues and Solutions

### Issue: Workflow fails at "Configure AWS Credentials"
**Solution**: Check that AWS secrets are added correctly in GitHub Settings

### Issue: Tests fail with accuracy below 75%
**Solution**: 
- Check if dataset was modified
- Retrain model locally: `python train_model.py`
- Verify model performance before pushing

### Issue: Docker build fails
**Solution**: 
- Check that Dockerfile exists in docker-lambda/
- Verify model files are being copied correctly
- Check ECR repository exists

### Issue: Lambda update fails
**Solution**:
- Verify Lambda function name matches workflow
- Check IAM permissions for Lambda
- Ensure ECR image was pushed successfully

## Monitoring and Logs

### View Workflow Logs
- Each job shows detailed logs
- Click on any step to expand details
- Download logs for debugging

### View Lambda Logs
```bash
# After deployment, check Lambda logs
aws logs tail /aws/lambda/customer-purchase-predictor --follow
```

### Check Deployment History
```bash
# List all deployment tags
git tag -l "deployment-*"

# View tag details
git show deployment-20251130-120000
```

## Rollback Process

If a deployment causes issues:

```bash
# Find previous successful deployment
git tag -l "deployment-*" | tail -2

# Get commit SHA from tag
PREVIOUS_SHA=$(git rev-list -n 1 deployment-20251129-120000)

# Update Lambda to previous image
aws lambda update-function-code \
  --function-name customer-purchase-predictor \
  --image-uri 295470186437.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-predictor:$PREVIOUS_SHA

# Wait for update
aws lambda wait function-updated \
  --function-name customer-purchase-predictor
```

## Cost Estimate

### GitHub Actions
- **Free tier**: 2,000 minutes/month
- **This workflow**: ~8 minutes per run
- **Capacity**: ~250 deployments/month free

### AWS Costs
- Lambda, ECR, S3 charges apply as usual
- No additional costs from CI/CD

## Best Practices

1. ✅ Always test locally before pushing
2. ✅ Write meaningful commit messages
3. ✅ Monitor workflow status after push
4. ✅ Keep AWS credentials secure (never commit them)
5. ✅ Review test results before deployment
6. ✅ Tag important deployments for easy rollback
7. ✅ Document any workflow changes

## Add Status Badge to README

Show pipeline status in your README:

```markdown
![ML Pipeline](https://github.com/futurexskill/deploy-model/actions/workflows/ml-pipeline.yml/badge.svg)
```

This displays: ![ML Pipeline](https://github.com/futurexskill/deploy-model/actions/workflows/ml-pipeline.yml/badge.svg)

## Next Steps

Once the basic pipeline is working:

1. **Add Slack notifications** for deployment status
2. **Implement blue-green deployments** for zero-downtime
3. **Add model performance monitoring** with CloudWatch
4. **Set up automatic rollback** on errors
5. **Create staging environment** for testing before production
6. **Add model versioning** in S3
7. **Implement A/B testing** for model comparison

## Getting Help

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Review AWS CloudWatch logs
3. Test commands locally first
4. Verify all AWS resources exist
5. Check IAM permissions

## Success Checklist

- [ ] AWS secrets added to GitHub
- [ ] Workflow file committed and pushed
- [ ] First workflow run completed successfully
- [ ] Lambda function updated with new model
- [ ] API endpoint tested and working
- [ ] Deployment tag created
- [ ] Status badge added to README

🎉 **Congratulations! Your ML CI/CD pipeline is ready!**

Every time you push code changes, your model will automatically:
1. Retrain with the latest code
2. Pass validation tests
3. Deploy to production
4. Be tested end-to-end

Your ML model deployment is now fully automated! 🚀
