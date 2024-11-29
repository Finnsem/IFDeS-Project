import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE  # Requires imbalanced-learn library
from sklearn.metrics import classification_report

# Load the dataset
data = pd.read_csv('app/static/data/data.csv')

# Handle NaN values by dropping them
data.dropna(inplace=True)

# Define the feature columns and the target column
X = data[['IsRegistered', 'YearsInOperation', 'HighReturns', 'TransparentBusinessModel', 
          'AccessibleManagement', 'ClearTerms', 'EasyWithdrawal', 'RequiresRecruitment', 
          'ThirdPartyReviews', 'UnsolicitedOffers', 'ProfessionalWebsite', 'EncouragesSecrecy']]
y = data['Flag']

# Convert categorical and boolean data to numerical data
X = pd.get_dummies(X, drop_first=True)

# Ensure all features are numeric
X = X.applymap(lambda x: int(x) if isinstance(x, bool) else x)

# Handle class imbalance with SMOTE
smote = SMOTE(k_neighbors=1)  # Set k_neighbors to 1

# Apply SMOTE
try:
    X_resampled, y_resampled = smote.fit_resample(X, y)
except ValueError as e:
    print(f"SMOTE Error: {e}")
    # Handle the case where SMOTE cannot be applied

# Split the data into training and testing sets with stratification
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42, stratify=y_resampled)

# Train a RandomForestClassifier model with balanced class weights
model = RandomForestClassifier(random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
print(classification_report(y_test, y_pred, zero_division=0))

# Save the trained model to a file (optional)
import joblib
joblib.dump(model, 'app/static/data/risk_model.pkl')
