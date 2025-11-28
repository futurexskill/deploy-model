from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load model and scaler at startup
try:
    model = joblib.load('purchase_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✓ Model and scaler loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None
    scaler = None


@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Customer Purchase Prediction API',
        'version': '1.0',
        'status': 'running',
        'model': 'Random Forest Classifier',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /predict': 'Make a prediction',
            'POST /predict/batch': 'Make batch predictions'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    model_loaded = model is not None and scaler is not None
    return jsonify({
        'status': 'healthy' if model_loaded else 'unhealthy',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict purchase probability for a single customer
    
    Expected JSON payload:
    {
        "age": 35,
        "salary": 50000
    }
    """
    try:
        # Check if model is loaded
        if model is None or scaler is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'Please ensure model files exist'
            }), 500
        
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Please send JSON data with age and salary'
            }), 400
        
        # Validate required fields
        if 'age' not in data or 'salary' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Both age and salary are required',
                'example': {'age': 35, 'salary': 50000}
            }), 400
        
        # Extract and validate data
        try:
            age = float(data['age'])
            salary = float(data['salary'])
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid data type',
                'message': 'Age and salary must be numeric values'
            }), 400
        
        # Validate ranges
        if age < 0 or age > 120:
            return jsonify({
                'error': 'Invalid age',
                'message': 'Age must be between 0 and 120'
            }), 400
        
        if salary < 0:
            return jsonify({
                'error': 'Invalid salary',
                'message': 'Salary must be a positive value'
            }), 400
        
        # Prepare input data
        input_data = np.array([[age, salary]])
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        probabilities = model.predict_proba(input_scaled)[0]
        
        # Prepare response
        result = {
            'input': {
                'age': age,
                'salary': salary
            },
            'prediction': {
                'will_purchase': bool(prediction == 1),
                'label': 'Will Purchase' if prediction == 1 else 'Will Not Purchase',
                'confidence': float(probabilities[1] if prediction == 1 else probabilities[0]),
                'probabilities': {
                    'not_purchase': float(probabilities[0]),
                    'purchase': float(probabilities[1])
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict purchase probability for multiple customers
    
    Expected JSON payload:
    {
        "customers": [
            {"age": 35, "salary": 50000},
            {"age": 25, "salary": 30000},
            {"age": 45, "salary": 75000}
        ]
    }
    """
    try:
        # Check if model is loaded
        if model is None or scaler is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'Please ensure model files exist'
            }), 500
        
        # Get JSON data
        data = request.get_json()
        
        if not data or 'customers' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide a "customers" array',
                'example': {
                    'customers': [
                        {'age': 35, 'salary': 50000},
                        {'age': 25, 'salary': 30000}
                    ]
                }
            }), 400
        
        customers = data['customers']
        
        if not isinstance(customers, list) or len(customers) == 0:
            return jsonify({
                'error': 'Invalid customers data',
                'message': 'customers must be a non-empty array'
            }), 400
        
        # Process each customer
        results = []
        errors = []
        
        for idx, customer in enumerate(customers):
            try:
                age = float(customer.get('age', 0))
                salary = float(customer.get('salary', 0))
                
                # Validate
                if age < 0 or age > 120 or salary < 0:
                    errors.append({
                        'index': idx,
                        'error': 'Invalid values',
                        'data': customer
                    })
                    continue
                
                # Prepare and predict
                input_data = np.array([[age, salary]])
                input_scaled = scaler.transform(input_data)
                prediction = model.predict(input_scaled)[0]
                probabilities = model.predict_proba(input_scaled)[0]
                
                results.append({
                    'index': idx,
                    'input': {
                        'age': age,
                        'salary': salary
                    },
                    'prediction': {
                        'will_purchase': bool(prediction == 1),
                        'label': 'Will Purchase' if prediction == 1 else 'Will Not Purchase',
                        'confidence': float(probabilities[1] if prediction == 1 else probabilities[0]),
                        'probabilities': {
                            'not_purchase': float(probabilities[0]),
                            'purchase': float(probabilities[1])
                        }
                    }
                })
                
            except Exception as e:
                errors.append({
                    'index': idx,
                    'error': str(e),
                    'data': customer
                })
        
        return jsonify({
            'total': len(customers),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors if errors else None,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'POST /predict',
            'POST /predict/batch'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print("=" * 70)
    print("CUSTOMER PURCHASE PREDICTION API")
    print("=" * 70)
    print("Starting server...")
    print("\nAPI Endpoints:")
    print("  GET  http://127.0.0.1:5001/           - API info")
    print("  GET  http://127.0.0.1:5001/health     - Health check")
    print("  POST http://127.0.0.1:5001/predict    - Single prediction")
    print("  POST http://127.0.0.1:5001/predict/batch - Batch predictions")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    
    app.run(debug=True, host='127.0.0.1', port=5001)
