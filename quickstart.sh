#!/bin/bash

# Quick Start Guide for Customer Purchase Prediction Model

echo "=================================================="
echo "CUSTOMER PURCHASE PREDICTION - QUICK START"
echo "=================================================="
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment activated!"
echo ""
echo "Available commands:"
echo ""
echo "1. Explore the data:"
echo "   python explore_data.py"
echo ""
echo "2. Train the model (already done):"
echo "   python train_model.py"
echo ""
echo "3. Make predictions:"
echo "   python predict.py <age> <salary>"
echo ""
echo "Examples:"
echo "   python predict.py 25 30000    # Young, low salary"
echo "   python predict.py 45 75000    # Middle age, high salary"
echo "   python predict.py 35 50000    # Middle age, medium salary"
echo ""
echo "4. Interactive mode:"
echo "   python predict.py"
echo ""
echo "=================================================="
