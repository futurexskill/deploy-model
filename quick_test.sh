#!/bin/bash

# Quick API Test - Run this in a NEW terminal while the API is running

echo "Testing Customer Purchase Prediction API..."
echo ""

# Test 1: Check if API is running
echo "1. Checking API health..."
curl -s http://127.0.0.1:5001/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Make a prediction
echo "2. Testing prediction (Age: 35, Salary: 50000)..."
curl -s -X POST http://127.0.0.1:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "salary": 50000}' | python3 -m json.tool
echo ""
echo ""

echo "3. Testing prediction (Age: 25, Salary: 30000)..."
curl -s -X POST http://127.0.0.1:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 25, "salary": 30000}' | python3 -m json.tool
echo ""
echo ""

echo "4. Testing batch prediction..."
curl -s -X POST http://127.0.0.1:5001/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"age": 25, "salary": 30000}, {"age": 45, "salary": 75000}]}' | python3 -m json.tool

echo ""
echo "✓ Tests complete!"
