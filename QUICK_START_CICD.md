# GitHub Actions CI/CD Pipeline - Quick Reference

## 🚀 What You Just Got

A fully automated ML deployment pipeline that:
- ✅ Trains your model on every code push
- ✅ Runs 8 validation tests before deployment
- ✅ Deploys to AWS Lambda automatically
- ✅ Tests the deployed API endpoint
- ✅ Blocks bad models from production

## ⚡ Quick Setup (3 Steps)

### 1. Add AWS Secrets to GitHub
```
Go to: https://github.com/futurexskill/deploy-model/settings/secrets/actions

Add two secrets:
- AWS_ACCESS_KEY_ID: (your AWS access key)
- AWS_SECRET_ACCESS_KEY: (your AWS secret key)
```

Get your AWS credentials:
```bash
aws configure get aws_access_key_id
aws configure get aws_secret_access_key
```

### 2. That's It! (Already Done)
The workflow file is already pushed to GitHub. It will run automatically on next push.

### 3. Test It
```bash
# Make a small change
echo "# CI/CD test" >> train_model.py

# Push to trigger workflow
git add train_model.py
git commit -m "Test CI/CD pipeline"
git push origin main
```

## 📊 Monitor Your Pipeline

**View runs**: https://github.com/futurexskill/deploy-model/actions

You'll see:
1. ⚙️ Train Model (uploads .pkl files)
2. 🧪 Test Model (8 validation tests)
3. 🚀 Deploy to AWS (S3 + ECR + Lambda)

## 🎯 What Gets Tested

| Test | What It Checks | Why It Matters |
|------|---------------|----------------|
| Files Exist | Model .pkl files created | Catches training failures |
| Model Loads | Can load from disk | Prevents broken deployments |
| Model Type | RandomForestClassifier | Ensures correct algorithm |
| Predictions | Valid outputs 0-1 | Catches logic errors |
| Performance | Accuracy >= 75% | Maintains quality standards |
| Consistency | Same input = same output | Ensures reproducibility |

## 🔄 Pipeline Triggers

Runs automatically when you push changes to:
- `*.py` - Any Python file
- `*.csv` - Any data file
- `requirements.txt` - Dependencies
- Workflow file itself

Or trigger manually:
1. Go to Actions tab
2. Select "ML Model CI/CD Pipeline"
3. Click "Run workflow"

## 📋 What Happens in Each Job

### Job 1: Train Model (~2-3 min)
```
✓ Checkout code
✓ Setup Python 3.11
✓ Install dependencies
✓ Run train_model.py
✓ Upload purchase_model.pkl & scaler.pkl
```

### Job 2: Test Model (~1 min)
```
✓ Download trained models
✓ Run 8 validation tests
✓ Check accuracy >= 75%
✓ Generate test report
→ If tests fail, STOP (no deployment)
```

### Job 3: Deploy to AWS (~5-7 min)
```
✓ Upload models to S3
✓ Build Docker image with models
✓ Push image to ECR
✓ Update Lambda function
✓ Test deployed endpoint
✓ Create deployment tag
```

## ✅ Success Indicators

**In GitHub Actions:**
- All jobs show green checkmarks ✅
- "Deployment Complete!" message appears
- New deployment tag created

**Test Your API:**
```bash
curl -X POST https://2y2wvahuza.execute-api.us-east-1.amazonaws.com \
  -H 'Content-Type: application/json' \
  -d '{"age": 35, "salary": 70000}'

# Should return updated predictions
```

## ❌ If Something Fails

### Training Fails
- Check if dataset file exists
- Verify dependencies in requirements.txt
- Test locally: `python train_model.py`

### Tests Fail
- Review test output in Actions log
- Check model accuracy (must be >= 75%)
- Run tests locally: `python tests/test_model.py`

### Deployment Fails
- Verify AWS secrets are set in GitHub
- Check AWS resources exist (S3, ECR, Lambda)
- Review IAM permissions

## 🔙 Rollback

If deployed model has issues:

```bash
# Find previous deployment
git tag -l "deployment-*" | tail -2

# Get commit SHA
PREV_SHA=$(git rev-list -n 1 deployment-20251129-120000)

# Rollback Lambda
aws lambda update-function-code \
  --function-name customer-purchase-predictor \
  --image-uri 295470186437.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-predictor:$PREV_SHA
```

## 📈 Add Status Badge

Show pipeline status in README.md:

```markdown
![ML Pipeline](https://github.com/futurexskill/deploy-model/actions/workflows/ml-pipeline.yml/badge.svg)
```

## 💰 Cost

- **GitHub Actions**: FREE (2,000 min/month)
- **This pipeline**: ~8 min per run
- **Capacity**: ~250 deployments/month free
- **AWS costs**: Same as before (minimal)

## 🎓 Learning Resources

- **Workflow file**: `.github/workflows/ml-pipeline.yml`
- **Test script**: `tests/test_model.py`
- **Full guide**: `CICD_SETUP.md`
- **Workflow docs**: `.github/workflows/README.md`

## 🚀 What's Automated Now

| Before | After |
|--------|-------|
| Manual training | ✅ Automatic on push |
| No validation | ✅ 8 automated tests |
| Manual S3 upload | ✅ Automatic upload |
| Manual Docker build | ✅ Automatic build |
| Manual Lambda update | ✅ Automatic update |
| Manual testing | ✅ Automatic endpoint test |
| No versioning | ✅ Deployment tags |

## 🎯 Next Time You Update Model

Just edit code and push:
```bash
# Edit your training code
vim train_model.py

# Commit and push
git add train_model.py
git commit -m "Improve model accuracy"
git push origin main

# That's it! Pipeline handles the rest
```

Watch it deploy automatically at:
https://github.com/futurexskill/deploy-model/actions

## 🎉 You're Done!

Your ML model now has:
- ✅ Continuous Integration (automated testing)
- ✅ Continuous Deployment (automated releases)
- ✅ Quality gates (tests block bad code)
- ✅ Version control (deployment tags)
- ✅ End-to-end automation

**Every code push = Production deployment (if tests pass)**

Welcome to modern ML DevOps! 🚀

---

**Questions?** Review `CICD_SETUP.md` for detailed setup and troubleshooting.
