# Tests Directory

This directory contains automated tests for the ML model CI/CD pipeline.

## Test Files

### `test_model.py`
Comprehensive validation tests that run before deployment:

1. **File Existence**: Verifies model files are created
2. **Model Loading**: Checks models can be loaded from disk
3. **Type Validation**: Confirms correct model types
4. **Attribute Checks**: Validates model methods and properties
5. **Prediction Tests**: Tests with known inputs
6. **Performance Metrics**: Ensures accuracy >= 75%
7. **Consistency**: Verifies reproducible predictions

## Running Tests Locally

```bash
# Install dependencies
pip install scikit-learn pandas numpy joblib pytest

# Train model first
python train_model.py

# Run tests
python tests/test_model.py
```

## CI/CD Integration

These tests run automatically in GitHub Actions:
- Triggered on every code push
- Must pass before deployment
- Blocks bad models from reaching production

## Adding New Tests

To add more tests, edit `test_model.py`:

```python
def test_your_new_test():
    """Description of your test"""
    print("\n🔍 Test X: Testing something...")
    
    # Your test logic here
    assert condition, "❌ Test failed message"
    
    print("✅ Test passed!")
```

Then add it to `run_all_tests()`:
```python
def run_all_tests():
    # ... existing tests ...
    test_your_new_test()
```

## Test Output

Tests provide clear output:
```
🔍 Test 1: Checking if model files exist...
✅ Model files exist

🔍 Test 2: Loading model and scaler...
✅ Model and scaler loaded successfully
```

## Performance Thresholds

Current minimum requirements:
- **Accuracy**: >= 75%
- **Prediction Range**: 0.0 to 1.0
- **Consistency**: Same input → Same output

Adjust these in `test_model.py` as needed.
