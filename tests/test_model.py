"""
Model Validation Tests for CI/CD Pipeline

This script tests the trained ML model to ensure it meets quality standards
before deployment to production.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def test_model_files_exist():
    """Test that model files exist"""
    print("\n🔍 Test 1: Checking if model files exist...")
    
    assert os.path.exists('purchase_model.pkl'), "❌ Model file not found!"
    assert os.path.exists('scaler.pkl'), "❌ Scaler file not found!"
    
    print("✅ Model files exist")

def test_model_loading():
    """Test that model and scaler can be loaded"""
    print("\n🔍 Test 2: Loading model and scaler...")
    
    try:
        model = joblib.load('purchase_model.pkl')
        scaler = joblib.load('scaler.pkl')
        print("✅ Model and scaler loaded successfully")
        return model, scaler
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)

def test_model_type(model):
    """Test that model is the expected type"""
    print("\n🔍 Test 3: Checking model type...")
    
    from sklearn.ensemble import RandomForestClassifier
    assert isinstance(model, RandomForestClassifier), "❌ Model is not RandomForestClassifier!"
    
    print("✅ Model type is correct (RandomForestClassifier)")

def test_model_attributes(model):
    """Test that model has expected attributes"""
    print("\n🔍 Test 4: Checking model attributes...")
    
    assert hasattr(model, 'predict'), "❌ Model doesn't have predict method!"
    assert hasattr(model, 'predict_proba'), "❌ Model doesn't have predict_proba method!"
    assert model.n_features_in_ == 2, f"❌ Model expects {model.n_features_in_} features, should be 2!"
    
    print("✅ Model has correct attributes")

def test_scaler_attributes(scaler):
    """Test that scaler has expected attributes"""
    print("\n🔍 Test 5: Checking scaler attributes...")
    
    from sklearn.preprocessing import StandardScaler
    assert isinstance(scaler, StandardScaler), "❌ Scaler is not StandardScaler!"
    assert hasattr(scaler, 'transform'), "❌ Scaler doesn't have transform method!"
    assert len(scaler.mean_) == 2, "❌ Scaler should have 2 features!"
    
    print("✅ Scaler has correct attributes")

def test_predictions(model, scaler):
    """Test model predictions with known inputs"""
    print("\n🔍 Test 6: Testing predictions with known inputs...")
    
    # Test cases with expected outcomes
    test_cases = [
        # (age, salary, expected_prediction_range)
        (35, 70000, (0.7, 1.0)),  # High salary, should likely purchase
        (20, 25000, (0.0, 0.3)),  # Low salary, should likely not purchase
        (45, 90000, (0.7, 1.0)),  # High salary, should likely purchase
        (25, 30000, (0.0, 0.5)),  # Low salary, should likely not purchase
    ]
    
    for age, salary, expected_range in test_cases:
        features = np.array([[age, salary]])
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0][1]
        
        print(f"  Input: Age={age}, Salary=${salary}")
        print(f"  Prediction: {prediction}, Probability: {probability:.2%}")
        
        # Verify prediction is binary
        assert prediction in [0, 1], f"❌ Invalid prediction: {prediction}"
        
        # Verify probability is in valid range
        assert 0 <= probability <= 1, f"❌ Invalid probability: {probability}"
        
        # Verify probability matches expected range (loose check)
        if prediction == 1:
            assert probability >= 0.5, f"❌ Prediction is 1 but probability is {probability}"
        else:
            assert probability < 0.5, f"❌ Prediction is 0 but probability is {probability}"
    
    print("✅ All predictions are valid")

def test_model_performance():
    """Test model performance on validation data"""
    print("\n🔍 Test 7: Testing model performance...")
    
    # Check if dataset exists
    if not os.path.exists('storepurchasedata_large.csv'):
        print("⚠️  Dataset not found, skipping performance test")
        return
    
    # Load dataset
    df = pd.read_csv('storepurchasedata_large.csv')
    X = df[['Age', 'Salary']].values
    y = df['Purchased'].values
    
    # Load model and scaler
    model = joblib.load('purchase_model.pkl')
    scaler = joblib.load('scaler.pkl')
    
    # Make predictions
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    
    # Calculate metrics
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    print(f"  Accuracy:  {accuracy:.2%}")
    print(f"  Precision: {precision:.2%}")
    print(f"  Recall:    {recall:.2%}")
    print(f"  F1 Score:  {f1:.2%}")
    
    # Assert minimum performance thresholds
    MIN_ACCURACY = 0.75  # At least 75% accuracy
    assert accuracy >= MIN_ACCURACY, f"❌ Accuracy {accuracy:.2%} is below minimum {MIN_ACCURACY:.2%}"
    
    print(f"✅ Model performance meets minimum threshold (accuracy >= {MIN_ACCURACY:.2%})")

def test_model_consistency():
    """Test that model gives consistent predictions"""
    print("\n🔍 Test 8: Testing prediction consistency...")
    
    model = joblib.load('purchase_model.pkl')
    scaler = joblib.load('scaler.pkl')
    
    # Same input should give same output
    test_input = np.array([[35, 70000]])
    test_input_scaled = scaler.transform(test_input)
    
    predictions = []
    for _ in range(5):
        pred = model.predict(test_input_scaled)[0]
        predictions.append(pred)
    
    # All predictions should be the same
    assert len(set(predictions)) == 1, "❌ Model gives inconsistent predictions!"
    
    print("✅ Model predictions are consistent")

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("🧪 STARTING MODEL VALIDATION TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Check files exist
        test_model_files_exist()
        
        # Test 2: Load model
        model, scaler = test_model_loading()
        
        # Test 3: Check model type
        test_model_type(model)
        
        # Test 4: Check model attributes
        test_model_attributes(model)
        
        # Test 5: Check scaler attributes
        test_scaler_attributes(scaler)
        
        # Test 6: Test predictions
        test_predictions(model, scaler)
        
        # Test 7: Test performance
        test_model_performance()
        
        # Test 8: Test consistency
        test_model_consistency()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🚀 Model is ready for deployment!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\n🛑 Deployment blocked due to test failure!")
        return 1
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("\n🛑 Deployment blocked due to error!")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
