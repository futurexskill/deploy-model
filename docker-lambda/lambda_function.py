import json
import joblib
import numpy as np
import os

# Load models at cold start (outside handler for reuse)
MODEL_PATH = 'purchase_model.pkl'
SCALER_PATH = 'scaler.pkl'

print(f"Loading model from {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print(f"Loading scaler from {SCALER_PATH}")
scaler = joblib.load(SCALER_PATH)
print("Models loaded successfully")

def lambda_handler(event, context):
    """
    AWS Lambda handler for customer purchase predictions
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Handle batch predictions
        if 'customers' in body:
            customers = body['customers']
            predictions = []
            
            for customer in customers:
                age = customer.get('age')
                salary = customer.get('salary')
                
                if age is None or salary is None:
                    predictions.append({
                        'error': 'Missing age or salary',
                        'customer': customer
                    })
                    continue
                
                # Make prediction
                features = np.array([[age, salary]])
                features_scaled = scaler.transform(features)
                prediction = int(model.predict(features_scaled)[0])
                probability = float(model.predict_proba(features_scaled)[0][1])
                
                predictions.append({
                    'age': age,
                    'salary': salary,
                    'will_purchase': bool(prediction),
                    'confidence': round(probability * 100, 2)
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'predictions': predictions,
                    'count': len(predictions)
                })
            }
        
        # Handle single prediction
        age = body.get('age')
        salary = body.get('salary')
        
        if age is None or salary is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required fields: age and salary'
                })
            }
        
        # Make prediction
        features = np.array([[age, salary]])
        features_scaled = scaler.transform(features)
        prediction = int(model.predict(features_scaled)[0])
        probability = float(model.predict_proba(features_scaled)[0][1])
        
        result = {
            'age': age,
            'salary': salary,
            'will_purchase': bool(prediction),
            'confidence': round(probability * 100, 2),
            'message': f"Customer {'will' if prediction else 'will not'} likely purchase (confidence: {round(probability * 100, 2)}%)"
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
