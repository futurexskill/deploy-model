import joblib
import numpy as np
import json
from sklearn.ensemble import RandomForestClassifier
import tensorflowjs as tfjs
import tensorflow as tf
from tensorflow import keras

# Load the trained model and scaler
print("Loading model and scaler...")
model = joblib.load('purchase_model.pkl')
scaler = joblib.load('scaler.pkl')

print(f"Model type: {type(model).__name__}")
print(f"Scaler mean: {scaler.mean_}")
print(f"Scaler scale: {scaler.scale_}")

# Save scaler parameters for JavaScript
scaler_params = {
    'mean': scaler.mean_.tolist(),
    'scale': scaler.scale_.tolist()
}

with open('scaler_params.json', 'w') as f:
    json.dump(scaler_params, f, indent=2)

print("\n✓ Scaler parameters saved to scaler_params.json")

# Since RandomForest doesn't directly convert to TensorFlow.js,
# we'll create a neural network that mimics the behavior
print("\nTraining a neural network to mimic the Random Forest...")

# Load the training data
import pandas as pd
df = pd.read_csv('storepurchasedata_large.csv')
X = df[['Age', 'Salary']].values
y = df['Purchased'].values

# Scale the data
X_scaled = scaler.transform(X)

# Get Random Forest predictions as training labels
rf_predictions = model.predict_proba(X_scaled)

# Create a neural network
nn_model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(2,)),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(2, activation='softmax')
])

nn_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Train the neural network
print("\nTraining neural network...")
history = nn_model.fit(
    X_scaled, y,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)

# Evaluate
train_accuracy = nn_model.evaluate(X_scaled, y, verbose=0)[1]
print(f"\nNeural Network Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")

# Compare with Random Forest
rf_accuracy = model.score(X_scaled, y)
print(f"Random Forest Accuracy: {rf_accuracy:.4f} ({rf_accuracy*100:.2f}%)")

# Save the model in TensorFlow.js format
print("\nSaving model in TensorFlow.js format...")
tfjs.converters.save_keras_model(nn_model, 'tfjs_model')

print("\n✓ Model saved to 'tfjs_model' directory")
print("\nFiles created:")
print("  - tfjs_model/model.json")
print("  - tfjs_model/group1-shard1of1.bin")
print("  - scaler_params.json")
print("\n✓ Model is ready for browser deployment!")
