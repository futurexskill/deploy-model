#!/bin/bash

# Read API endpoint from file or use argument
if [ -f "api_endpoint.txt" ]; then
    API_ENDPOINT=$(cat api_endpoint.txt)
elif [ -n "$1" ]; then
    API_ENDPOINT=$1
else
    echo "Usage: $0 [API_ENDPOINT]"
    echo "Or create api_endpoint.txt with your endpoint"
    exit 1
fi

echo "Testing Lambda API at: $API_ENDPOINT"
echo ""

# Test 1: Single prediction - likely to purchase
echo "Test 1: Customer likely to purchase (Age: 35, Salary: 70000)"
curl -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"age": 35, "salary": 70000}' | jq '.'
echo ""
echo ""

# Test 2: Single prediction - unlikely to purchase
echo "Test 2: Customer unlikely to purchase (Age: 20, Salary: 25000)"
curl -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"age": 20, "salary": 25000}' | jq '.'
echo ""
echo ""

# Test 3: Batch predictions
echo "Test 3: Batch predictions"
curl -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{
        "customers": [
            {"age": 25, "salary": 30000},
            {"age": 40, "salary": 80000},
            {"age": 30, "salary": 55000},
            {"age": 50, "salary": 90000}
        ]
    }' | jq '.'
echo ""
echo ""

# Test 4: Error handling - missing fields
echo "Test 4: Error handling - missing fields"
curl -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"age": 30}' | jq '.'
echo ""
echo ""

echo "All tests completed!"
