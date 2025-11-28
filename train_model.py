import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('storepurchasedata_large.csv')

# Prepare features and target
X = df[['Age', 'Salary']].values
y = df['Purchased'].values

print(f"Dataset shape: {X.shape}")
print(f"Features: Age, Salary")
print(f"Target: Purchased (0 = No, 1 = Yes)")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nTraining samples: {X_train.shape[0]}")
print(f"Testing samples: {X_test.shape[0]}")

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n" + "=" * 70)
print("TRAINING MULTIPLE MODELS")
print("=" * 70)

# Dictionary to store models and their scores
models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'SVM (RBF Kernel)': SVC(kernel='rbf', random_state=42)
}

results = {}

# Train and evaluate each model
for model_name, model in models.items():
    print(f"\n{'-' * 70}")
    print(f"Training {model_name}...")
    
    # Train the model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Calculate accuracy
    train_accuracy = accuracy_score(y_train, y_pred_train)
    test_accuracy = accuracy_score(y_test, y_pred_test)
    
    results[model_name] = {
        'model': model,
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy,
        'predictions': y_pred_test
    }
    
    print(f"Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    print(f"Testing Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")

# Find the best model
best_model_name = max(results, key=lambda x: results[x]['test_accuracy'])
best_model = results[best_model_name]['model']
best_accuracy = results[best_model_name]['test_accuracy']

print("\n" + "=" * 70)
print(f"BEST MODEL: {best_model_name}")
print(f"Test Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
print("=" * 70)

# Detailed evaluation of the best model
y_pred_best = results[best_model_name]['predictions']

print("\n" + "-" * 70)
print("CLASSIFICATION REPORT (Best Model)")
print("-" * 70)
print(classification_report(y_test, y_pred_best, target_names=['Not Purchased', 'Purchased']))

print("\n" + "-" * 70)
print("CONFUSION MATRIX (Best Model)")
print("-" * 70)
cm = confusion_matrix(y_test, y_pred_best)
print(cm)

# Save the best model and scaler
joblib.dump(best_model, 'purchase_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("\n" + "=" * 70)
print(f"Best model saved as 'purchase_model.pkl'")
print(f"Scaler saved as 'scaler.pkl'")
print(f"Model Type: {best_model_name}")
print("=" * 70)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Model comparison
model_names = list(results.keys())
train_accuracies = [results[name]['train_accuracy'] for name in model_names]
test_accuracies = [results[name]['test_accuracy'] for name in model_names]

x = np.arange(len(model_names))
width = 0.35

axes[0, 0].bar(x - width/2, train_accuracies, width, label='Train Accuracy', color='skyblue')
axes[0, 0].bar(x + width/2, test_accuracies, width, label='Test Accuracy', color='orange')
axes[0, 0].set_ylabel('Accuracy')
axes[0, 0].set_title('Model Comparison: Training vs Testing Accuracy')
axes[0, 0].set_xticks(x)
axes[0, 0].set_xticklabels(model_names, rotation=45, ha='right')
axes[0, 0].legend()
axes[0, 0].set_ylim([0.7, 1.0])

# Confusion matrix heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 1],
            xticklabels=['Not Purchased', 'Purchased'],
            yticklabels=['Not Purchased', 'Purchased'])
axes[0, 1].set_title(f'Confusion Matrix - {best_model_name}')
axes[0, 1].set_ylabel('True Label')
axes[0, 1].set_xlabel('Predicted Label')

# Decision boundary visualization
h = 0.02
x_min, x_max = X_train_scaled[:, 0].min() - 1, X_train_scaled[:, 0].max() + 1
y_min, y_max = X_train_scaled[:, 1].min() - 1, X_train_scaled[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

Z = best_model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

axes[1, 0].contourf(xx, yy, Z, alpha=0.4, cmap='RdYlGn')
scatter = axes[1, 0].scatter(X_test_scaled[:, 0], X_test_scaled[:, 1], 
                             c=y_test, cmap='RdYlGn', edgecolors='black', s=50)
axes[1, 0].set_title(f'Decision Boundary - {best_model_name}')
axes[1, 0].set_xlabel('Age (scaled)')
axes[1, 0].set_ylabel('Salary (scaled)')
plt.colorbar(scatter, ax=axes[1, 0], label='Purchased')

# Accuracy comparison plot
axes[1, 1].plot(model_names, test_accuracies, marker='o', linestyle='-', linewidth=2, 
               markersize=10, color='green')
axes[1, 1].set_ylabel('Test Accuracy')
axes[1, 1].set_title('Model Performance on Test Set')
axes[1, 1].set_xticklabels(model_names, rotation=45, ha='right')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_ylim([min(test_accuracies) - 0.05, 1.0])

plt.tight_layout()
plt.savefig('model_training_results.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'model_training_results.png'")

print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETE!")
print("=" * 70)
