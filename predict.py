import joblib
import numpy as np
import sys

def predict_purchase(age, salary):
    """
    Predict whether a customer will make a purchase based on age and salary.
    
    Parameters:
    -----------
    age : int or float
        Customer's age
    salary : int or float
        Customer's annual salary
    
    Returns:
    --------
    prediction : int
        0 = Will not purchase, 1 = Will purchase
    probability : float
        Probability of making a purchase (if model supports it)
    """
    try:
        # Load the trained model and scaler
        model = joblib.load('purchase_model.pkl')
        scaler = joblib.load('scaler.pkl')
        
        # Prepare the input data
        input_data = np.array([[age, salary]])
        
        # Scale the input data
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        
        # Try to get prediction probability if model supports it
        try:
            probabilities = model.predict_proba(input_scaled)[0]
            probability = probabilities[1]  # Probability of purchasing (class 1)
        except AttributeError:
            # Some models don't support predict_proba
            probability = None
        
        return prediction, probability
    
    except FileNotFoundError:
        print("Error: Model files not found. Please train the model first by running 'train_model.py'")
        sys.exit(1)
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        sys.exit(1)


def main():
    """
    Main function to handle command-line arguments or interactive input
    """
    print("=" * 70)
    print("CUSTOMER PURCHASE PREDICTION SYSTEM")
    print("=" * 70)
    
    # Check if command-line arguments are provided
    if len(sys.argv) == 3:
        try:
            age = float(sys.argv[1])
            salary = float(sys.argv[2])
        except ValueError:
            print("Error: Age and salary must be numeric values")
            sys.exit(1)
    else:
        # Interactive input
        print("\nEnter customer details:")
        try:
            age = float(input("Age: "))
            salary = float(input("Salary: "))
        except ValueError:
            print("Error: Please enter valid numeric values")
            sys.exit(1)
    
    # Validate inputs
    if age < 0 or age > 120:
        print("Warning: Age seems unusual (should be between 0 and 120)")
    if salary < 0:
        print("Warning: Salary should be a positive value")
    
    # Make prediction
    prediction, probability = predict_purchase(age, salary)
    
    # Display results
    print("\n" + "-" * 70)
    print("PREDICTION RESULTS")
    print("-" * 70)
    print(f"Customer Age: {age}")
    print(f"Customer Salary: ${salary:,.2f}")
    print()
    
    if prediction == 1:
        print("✓ PREDICTION: Customer WILL make a purchase")
    else:
        print("✗ PREDICTION: Customer will NOT make a purchase")
    
    if probability is not None:
        print(f"\nConfidence: {probability * 100:.2f}%")
        print(f"Purchase Probability: {probability:.4f}")
        print(f"No Purchase Probability: {1 - probability:.4f}")
    
    print("-" * 70)


if __name__ == "__main__":
    main()
