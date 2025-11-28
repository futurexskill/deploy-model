# API Documentation

## Customer Purchase Prediction REST API

A RESTful API for predicting customer purchase behavior based on age and salary using a Random Forest machine learning model.

### Base URL
```
http://127.0.0.1:5000
```

---

## Endpoints

### 1. Home - API Information
**Endpoint:** `GET /`

**Description:** Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Customer Purchase Prediction API",
  "version": "1.0",
  "status": "running",
  "model": "Random Forest Classifier",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "POST /predict": "Make a prediction",
    "POST /predict/batch": "Make batch predictions"
  }
}
```

---

### 2. Health Check
**Endpoint:** `GET /health`

**Description:** Check if the API and model are loaded and ready.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-11-28T10:00:00.000000"
}
```

---

### 3. Single Prediction
**Endpoint:** `POST /predict`

**Description:** Predict purchase probability for a single customer.

**Request Body:**
```json
{
  "age": 35,
  "salary": 50000
}
```

**Parameters:**
- `age` (number, required): Customer's age (0-120)
- `salary` (number, required): Customer's annual salary (positive number)

**Success Response (200):**
```json
{
  "input": {
    "age": 35,
    "salary": 50000
  },
  "prediction": {
    "will_purchase": true,
    "label": "Will Purchase",
    "confidence": 0.88,
    "probabilities": {
      "not_purchase": 0.12,
      "purchase": 0.88
    }
  },
  "timestamp": "2025-11-28T10:00:00.000000"
}
```

**Error Response (400):**
```json
{
  "error": "Missing required fields",
  "message": "Both age and salary are required",
  "example": {
    "age": 35,
    "salary": 50000
  }
}
```

**Example cURL:**
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "salary": 50000}'
```

**Example Python:**
```python
import requests

data = {"age": 35, "salary": 50000}
response = requests.post("http://127.0.0.1:5000/predict", json=data)
print(response.json())
```

---

### 4. Batch Prediction
**Endpoint:** `POST /predict/batch`

**Description:** Predict purchase probability for multiple customers at once.

**Request Body:**
```json
{
  "customers": [
    {"age": 25, "salary": 30000},
    {"age": 35, "salary": 50000},
    {"age": 45, "salary": 75000}
  ]
}
```

**Parameters:**
- `customers` (array, required): Array of customer objects with age and salary

**Success Response (200):**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "input": {
        "age": 25,
        "salary": 30000
      },
      "prediction": {
        "will_purchase": false,
        "label": "Will Not Purchase",
        "confidence": 0.69,
        "probabilities": {
          "not_purchase": 0.69,
          "purchase": 0.31
        }
      }
    },
    {
      "index": 1,
      "input": {
        "age": 35,
        "salary": 50000
      },
      "prediction": {
        "will_purchase": true,
        "label": "Will Purchase",
        "confidence": 0.88,
        "probabilities": {
          "not_purchase": 0.12,
          "purchase": 0.88
        }
      }
    }
  ],
  "errors": null,
  "timestamp": "2025-11-28T10:00:00.000000"
}
```

**Example cURL:**
```bash
curl -X POST http://127.0.0.1:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"age": 25, "salary": 30000},
      {"age": 45, "salary": 75000}
    ]
  }'
```

**Example Python:**
```python
import requests

data = {
    "customers": [
        {"age": 25, "salary": 30000},
        {"age": 45, "salary": 75000}
    ]
}
response = requests.post("http://127.0.0.1:5000/predict/batch", json=data)
print(response.json())
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Invalid endpoint |
| 500 | Internal Server Error - Server or model error |

---

## Common Error Responses

### Missing Required Fields
```json
{
  "error": "Missing required fields",
  "message": "Both age and salary are required",
  "example": {"age": 35, "salary": 50000}
}
```

### Invalid Data Type
```json
{
  "error": "Invalid data type",
  "message": "Age and salary must be numeric values"
}
```

### Invalid Age
```json
{
  "error": "Invalid age",
  "message": "Age must be between 0 and 120"
}
```

### Invalid Salary
```json
{
  "error": "Invalid salary",
  "message": "Salary must be a positive value"
}
```

---

## Testing

### Using cURL
```bash
# Test the API
curl http://127.0.0.1:5000/

# Make a prediction
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "salary": 50000}'
```

### Using Python Test Script
```bash
# Activate virtual environment
source venv/bin/activate

# Install requests library if not already installed
pip install requests

# Run test script
python test_api.py
```

### Using Bash Test Script
```bash
# Make script executable
chmod +x test_api.sh

# Run tests
./test_api.sh
```

---

## Running the API

### Start the Server
```bash
# Activate virtual environment
source venv/bin/activate

# Install Flask dependencies
pip install flask flask-cors

# Start the server
python app.py
```

The server will start on `http://127.0.0.1:5000`

### Stop the Server
Press `Ctrl+C` in the terminal where the server is running.

---

## Response Fields

### Prediction Object
- `will_purchase` (boolean): Whether the customer will purchase (true/false)
- `label` (string): Human-readable prediction label
- `confidence` (number): Confidence score for the prediction (0-1)
- `probabilities` (object):
  - `not_purchase` (number): Probability of not purchasing (0-1)
  - `purchase` (number): Probability of purchasing (0-1)

---

## Model Information

- **Algorithm**: Random Forest Classifier
- **Features**: Age, Salary
- **Target**: Purchase (Binary: 0/1)
- **Accuracy**: >90% on test data
- **Preprocessing**: StandardScaler normalization

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse.

---

## CORS

CORS (Cross-Origin Resource Sharing) is enabled for all routes, allowing the API to be called from web applications running on different domains.

---

## Development vs Production

This API is configured for **development/testing** purposes with:
- Debug mode enabled
- Running on localhost (127.0.0.1)
- No authentication
- No rate limiting

For **production** deployment, you should:
1. Disable debug mode
2. Use a production WSGI server (gunicorn, uWSGI)
3. Implement authentication (API keys, JWT)
4. Add rate limiting
5. Use HTTPS
6. Add logging and monitoring
7. Deploy to a cloud platform

---

## Support

For issues or questions, please refer to the main README.md or contact the repository maintainer.
