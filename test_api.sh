#!/bin/bash

# Test script for Customer Purchase Prediction API

API_URL="http://127.0.0.1:5000"

echo "======================================================================"
echo "CUSTOMER PURCHASE PREDICTION API - TEST SCRIPT"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Home endpoint
echo -e "${BLUE}Test 1: Home Endpoint${NC}"
echo "GET $API_URL/"
curl -X GET $API_URL/ | jq '.'
echo ""
echo ""

# Test 2: Health check
echo -e "${BLUE}Test 2: Health Check${NC}"
echo "GET $API_URL/health"
curl -X GET $API_URL/health | jq '.'
echo ""
echo ""

# Test 3: Single prediction - Will NOT purchase
echo -e "${BLUE}Test 3: Single Prediction - Young, Low Salary (Will NOT purchase)${NC}"
echo "POST $API_URL/predict"
echo 'Payload: {"age": 25, "salary": 30000}'
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 25, "salary": 30000}' | jq '.'
echo ""
echo ""

# Test 4: Single prediction - WILL purchase
echo -e "${BLUE}Test 4: Single Prediction - Mid-age, Good Salary (WILL purchase)${NC}"
echo "POST $API_URL/predict"
echo 'Payload: {"age": 45, "salary": 75000}'
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 45, "salary": 75000}' | jq '.'
echo ""
echo ""

# Test 5: Single prediction - Edge case
echo -e "${BLUE}Test 5: Single Prediction - Mid-age, Medium Salary${NC}"
echo "POST $API_URL/predict"
echo 'Payload: {"age": 35, "salary": 50000}'
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "salary": 50000}' | jq '.'
echo ""
echo ""

# Test 6: Batch prediction
echo -e "${BLUE}Test 6: Batch Prediction - Multiple Customers${NC}"
echo "POST $API_URL/predict/batch"
curl -X POST $API_URL/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"age": 25, "salary": 30000},
      {"age": 35, "salary": 50000},
      {"age": 45, "salary": 75000},
      {"age": 60, "salary": 90000},
      {"age": 28, "salary": 70000}
    ]
  }' | jq '.'
echo ""
echo ""

# Test 7: Error handling - Missing fields
echo -e "${BLUE}Test 7: Error Handling - Missing Required Fields${NC}"
echo "POST $API_URL/predict"
echo 'Payload: {"age": 25}'
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 25}' | jq '.'
echo ""
echo ""

# Test 8: Error handling - Invalid data
echo -e "${BLUE}Test 8: Error Handling - Invalid Age${NC}"
echo "POST $API_URL/predict"
echo 'Payload: {"age": -5, "salary": 50000}'
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": -5, "salary": 50000}' | jq '.'
echo ""
echo ""

echo -e "${GREEN}======================================================================"
echo "ALL TESTS COMPLETED!"
echo "======================================================================${NC}"
