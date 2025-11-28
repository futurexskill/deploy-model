import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv('storepurchasedata_large.csv')

# Display basic information
print("=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)
print(f"\nDataset Shape: {df.shape}")
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

print("\n" + "=" * 50)
print("FIRST FEW ROWS")
print("=" * 50)
print(df.head(10))

print("\n" + "=" * 50)
print("DATASET INFO")
print("=" * 50)
print(df.info())

print("\n" + "=" * 50)
print("STATISTICAL SUMMARY")
print("=" * 50)
print(df.describe())

print("\n" + "=" * 50)
print("MISSING VALUES")
print("=" * 50)
print(df.isnull().sum())

print("\n" + "=" * 50)
print("CLASS DISTRIBUTION")
print("=" * 50)
print(df['Purchased'].value_counts())
print(f"\nPercentage distribution:")
print(df['Purchased'].value_counts(normalize=True) * 100)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Age distribution by purchase status
axes[0, 0].hist([df[df['Purchased'] == 0]['Age'], df[df['Purchased'] == 1]['Age']], 
                bins=20, label=['Not Purchased', 'Purchased'], color=['red', 'green'], alpha=0.7)
axes[0, 0].set_xlabel('Age')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Age Distribution by Purchase Status')
axes[0, 0].legend()

# Salary distribution by purchase status
axes[0, 1].hist([df[df['Purchased'] == 0]['Salary'], df[df['Purchased'] == 1]['Salary']], 
                bins=20, label=['Not Purchased', 'Purchased'], color=['red', 'green'], alpha=0.7)
axes[0, 1].set_xlabel('Salary')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Salary Distribution by Purchase Status')
axes[0, 1].legend()

# Scatter plot
scatter = axes[1, 0].scatter(df['Age'], df['Salary'], c=df['Purchased'], 
                            cmap='RdYlGn', alpha=0.6, edgecolors='black')
axes[1, 0].set_xlabel('Age')
axes[1, 0].set_ylabel('Salary')
axes[1, 0].set_title('Age vs Salary (colored by Purchase Status)')
plt.colorbar(scatter, ax=axes[1, 0], label='Purchased')

# Purchase status count
purchase_counts = df['Purchased'].value_counts()
axes[1, 1].bar(['Not Purchased', 'Purchased'], purchase_counts.values, color=['red', 'green'], alpha=0.7)
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_title('Purchase Status Distribution')
axes[1, 1].set_xlabel('Purchase Status')

plt.tight_layout()
plt.savefig('data_exploration.png', dpi=300, bbox_inches='tight')
print("\n" + "=" * 50)
print("Visualization saved as 'data_exploration.png'")
print("=" * 50)
plt.show()
