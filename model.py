import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# Define dataset path
DATA_PATH = r"C:\Users\Aditya Vishwakarma\OneDrive\Desktop\project\datasets\data.csv"  # Update with actual path

# Check if the file exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Please verify the file path.")

# Load dataset
data = pd.read_csv(DATA_PATH)

# Convert the target column 'Attrition' to numeric
if 'Attrition' not in data.columns:
    raise ValueError("The 'Attrition' column is missing in the dataset.")
data['Attrition'] = data['Attrition'].map({'Yes': 1, 'No': 0})

# Check for missing values and handle them
if data.isnull().sum().sum() > 0:
    print("Warning: Dataset contains missing values. Filling them with median values.")
    data.fillna(data.median(numeric_only=True), inplace=True)

# Select features and target variable
FEATURES = ['Age', 'BusinessTravel', 'DailyRate', 'DistanceFromHome',
            'Education', 'Department', 'YearsAtCompany', 'WorkLifeBalance', 
            'YearsSinceLastPromotion']
if not all(feature in data.columns for feature in FEATURES):
    raise ValueError("One or more selected features are missing in the dataset.")

X = data[FEATURES]
y = data['Attrition']

# One-hot encode categorical features
X = pd.get_dummies(X, columns=['BusinessTravel', 'Department'], drop_first=True)

# Save the feature names for later use
feature_names = list(X.columns)
print("Feature Names after one-hot encoding:", feature_names)  # Debug

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the XGBoost model
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42, n_estimators=200)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Model Accuracy:", accuracy)
print("Classification Report:\n", classification_report(y_test, y_pred))

# Debug: Print feature importances
print("Feature Importances:")
for name, importance in zip(feature_names, model.feature_importances_):
    print(f"{name}: {importance}")

# Save the model and metadata
model_path = "model_metadata.pkl"
with open(model_path, "wb") as f:
    pickle.dump({'model': model, 'accuracy': accuracy, 'feature_names': feature_names}, f)

print(f"Model and metadata saved to {model_path}.")