# Customer Purchase Prediction Model

This project builds a machine learning model to predict whether a customer will make a purchase based on their age and salary.

## Dataset

- **Source**: [storepurchasedata_large.csv](https://github.com/futurexskill/ml-model-deployment/blob/main/storepurchasedata_large.csv)
- **Features**: 
  - Age: Customer's age
  - Salary: Customer's annual salary
- **Target**: 
  - Purchased: 0 (No) or 1 (Yes)

## Project Structure

```
model-deployment/
├── storepurchasedata_large.csv    # Dataset
├── explore_data.py                 # Data exploration script
├── train_model.py                  # Model training script
├── predict.py                      # Prediction script
├── purchase_model.pkl              # Trained model (generated)
├── scaler.pkl                      # Feature scaler (generated)
├── data_exploration.png            # Data visualizations (generated)
├── model_training_results.png      # Training results (generated)
└── README.md                       # This file
```

## Setup

### 1. Install Required Packages

```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

### 2. Explore the Data (Optional)

```bash
python explore_data.py
```

This will:
- Display dataset statistics
- Show data distribution
- Generate visualization plots
- Save results to `data_exploration.png`

### 3. Train the Model

```bash
python train_model.py
```

This will:
- Train multiple classification models (Logistic Regression, Decision Tree, Random Forest, SVM)
- Compare their performance
- Select the best model
- Save the trained model and scaler
- Generate performance visualizations

The script will create:
- `purchase_model.pkl`: The best trained model
- `scaler.pkl`: Feature scaler for preprocessing
- `model_training_results.png`: Visualization of training results

## Usage

### Make Predictions

#### Method 1: Interactive Mode

```bash
python predict.py
```

The script will prompt you to enter age and salary.

#### Method 2: Command-Line Arguments

```bash
python predict.py <age> <salary>
```

**Examples:**

```bash
# Predict for a 25-year-old with $30,000 salary
python predict.py 25 30000

# Predict for a 45-year-old with $75,000 salary
python predict.py 45 75000

# Predict for a 35-year-old with $60,000 salary
python predict.py 35 60000
```

### Example Output

```
======================================================================
CUSTOMER PURCHASE PREDICTION SYSTEM
======================================================================

----------------------------------------------------------------------
PREDICTION RESULTS
----------------------------------------------------------------------
Customer Age: 35
Customer Salary: $60,000.00

✓ PREDICTION: Customer WILL make a purchase

Confidence: 85.32%
Purchase Probability: 0.8532
No Purchase Probability: 0.1468
----------------------------------------------------------------------
```

## Model Performance

The training script compares multiple models:
- **Logistic Regression**: Linear classification model
- **Decision Tree**: Non-linear tree-based model
- **Random Forest**: Ensemble of decision trees
- **SVM (RBF Kernel)**: Support Vector Machine with radial basis function

The best performing model is automatically selected and saved.

## Files Generated

After running the scripts, the following files will be created:

1. **purchase_model.pkl**: Serialized trained model
2. **scaler.pkl**: Serialized feature scaler
3. **data_exploration.png**: Data visualization plots
4. **model_training_results.png**: Model comparison and performance plots

## Notes

- The model uses StandardScaler for feature normalization
- All predictions are made on scaled data
- The model achieves high accuracy on the test set (typically >90%)
- Input validation is performed to check for reasonable age and salary values

## License

This project is for educational purposes.
