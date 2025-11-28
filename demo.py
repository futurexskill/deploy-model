import joblib
import numpy as np
import pandas as pd

# Load the model and scaler
model = joblib.load('purchase_model.pkl')
scaler = joblib.load('scaler.pkl')

print("=" * 80)
print("CUSTOMER PURCHASE PREDICTION - BATCH DEMO")
print("=" * 80)

# Define test cases
test_cases = [
    {"age": 20, "salary": 25000, "description": "Young, entry-level"},
    {"age": 25, "salary": 30000, "description": "Young, low income"},
    {"age": 30, "salary": 45000, "description": "Young professional"},
    {"age": 35, "salary": 50000, "description": "Mid-career, moderate income"},
    {"age": 40, "salary": 60000, "description": "Established, good income"},
    {"age": 45, "salary": 70000, "description": "Senior professional"},
    {"age": 50, "salary": 80000, "description": "High earner"},
    {"age": 60, "salary": 90000, "description": "Senior, high income"},
    {"age": 65, "salary": 95000, "description": "Pre-retirement, peak earnings"},
    {"age": 28, "salary": 70000, "description": "Young high-earner"},
]

# Create results table
results = []

print("\nTesting various customer profiles:\n")
print("-" * 80)
print(f"{'Age':<6} {'Salary':<12} {'Description':<30} {'Prediction':<12} {'Confidence'}")
print("-" * 80)

for case in test_cases:
    age = case['age']
    salary = case['salary']
    desc = case['description']
    
    # Prepare input
    input_data = np.array([[age, salary]])
    input_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0]
    confidence = probability[1] if prediction == 1 else probability[0]
    
    # Store result
    result_text = "WILL BUY" if prediction == 1 else "Won't buy"
    
    results.append({
        'Age': age,
        'Salary': salary,
        'Description': desc,
        'Prediction': result_text,
        'Confidence': f"{confidence*100:.1f}%"
    })
    
    # Print result
    print(f"{age:<6} ${salary:<11,} {desc:<30} {result_text:<12} {confidence*100:>5.1f}%")

print("-" * 80)

# Summary statistics
will_buy = sum(1 for r in results if r['Prediction'] == 'WILL BUY')
wont_buy = len(results) - will_buy

print(f"\nSummary:")
print(f"  Total customers tested: {len(results)}")
print(f"  Predicted to purchase: {will_buy} ({will_buy/len(results)*100:.1f}%)")
print(f"  Predicted not to purchase: {wont_buy} ({wont_buy/len(results)*100:.1f}%)")

print("\n" + "=" * 80)
print("Key Observations:")
print("=" * 80)
print("✓ Higher age + higher salary = stronger purchase likelihood")
print("✓ Young customers with high salaries show strong purchase intent")
print("✓ Low salary customers are less likely to purchase regardless of age")
print("=" * 80)
