import os
import shutil
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb
from sklearn.metrics import accuracy_score

print("Setting up directory structure...")
os.makedirs("dataset", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

# Copy dataset.csv to dataset/loan.csv if it exists in current folder
if os.path.exists("dataset.csv") and not os.path.exists("dataset/loan.csv"):
    shutil.copy("dataset.csv", "dataset/loan.csv")
    print("Copied dataset.csv to dataset/loan.csv")

# Load dataset
df = pd.read_csv("dataset/loan.csv")
print(f"Dataset shape: {df.shape}")

# Drop loan_id
if 'loan_id' in df.columns:
    df = df.drop(columns=['loan_id'])

# Preprocessing & Imputation
df['gender'] = df['gender'].fillna(df['gender'].mode()[0])
df['married'] = df['married'].fillna(df['married'].mode()[0])
df['dependents'] = df['dependents'].fillna(df['dependents'].mode()[0])
df['education'] = df['education'].fillna(df['education'].mode()[0])
df['self_employed'] = df['self_employed'].fillna(df['self_employed'].mode()[0])
df['applicantincome'] = df['applicantincome'].fillna(df['applicantincome'].median())
df['coapplicantincome'] = df['coapplicantincome'].fillna(df['coapplicantincome'].median())
df['loanamount'] = df['loanamount'].fillna(df['loanamount'].median())
df['loan_amount_term'] = df['loan_amount_term'].fillna(df['loan_amount_term'].mode()[0])
df['credit_history'] = df['credit_history'].fillna(df['credit_history'].mode()[0])

# Feature Encoding
gender_map = {'male': 1, 'female': 0}
married_map = {'yes': 1, 'no': 0}
dependents_map = {'0': 0, '1': 1, '2': 2, '3+': 3}
education_map = {'graduate': 1, 'not graduate': 0}
self_employed_map = {'yes': 1, 'no': 0}
property_area_map = {'rural': 0, 'semiurban': 1, 'urban': 2}
loan_status_map = {'y': 1, 'n': 0}

df['gender'] = df['gender'].str.lower().map(gender_map)
df['married'] = df['married'].str.lower().map(married_map)
df['dependents'] = df['dependents'].astype(str).str.lower().map(dependents_map)
df['education'] = df['education'].str.lower().map(education_map)
df['self_employed'] = df['self_employed'].str.lower().map(self_employed_map)
df['property_area'] = df['property_area'].str.lower().map(property_area_map)
df['loan_status'] = df['loan_status'].str.lower().map(loan_status_map)

# Split features and target
X = df.drop(columns=['loan_status'])
y = df['loan_status']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

print("\nTraining models...")

# A. Decision Tree
dt = DecisionTreeClassifier(max_depth=4, random_state=0)
dt.fit(X_train, y_train)
dt_train_acc = accuracy_score(y_train, dt.predict(X_train))
dt_test_acc = accuracy_score(y_test, dt.predict(X_test))
print(f"Decision Tree - Train Acc: {dt_train_acc*100:.2f}%, Test Acc: {dt_test_acc*100:.2f}%")

# B. Random Forest
rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=0)
rf.fit(X_train, y_train)
rf_train_acc = accuracy_score(y_train, rf.predict(X_train))
rf_test_acc = accuracy_score(y_test, rf.predict(X_test))
print(f"Random Forest - Train Acc: {rf_train_acc*100:.2f}%, Test Acc: {rf_test_acc*100:.2f}%")

# C. KNN (Requires Scaling)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

knn = KNeighborsClassifier(n_neighbors=7)
knn.fit(X_train_scaled, y_train)
knn_train_acc = accuracy_score(y_train, knn.predict(X_train_scaled))
knn_test_acc = accuracy_score(y_test, knn.predict(X_test_scaled))
print(f"K-Nearest Neighbors - Train Acc: {knn_train_acc*100:.2f}%, Test Acc: {knn_test_acc*100:.2f}%")

# D. XGBoost
xgb_model = xgb.XGBClassifier(
    max_depth=5,
    n_estimators=80,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)
xgb_model.fit(X_train, y_train)
xgb_train_acc = accuracy_score(y_train, xgb_model.predict(X_train))
xgb_test_acc = accuracy_score(y_test, xgb_model.predict(X_test))
print(f"XGBoost - Train Acc: {xgb_train_acc*100:.2f}%, Test Acc: {xgb_test_acc*100:.2f}%")

# Save model both in Pickle and JSON booster format
with open("model.pkl", "wb") as f:
    pickle.dump(xgb_model, f)
xgb_model.save_model("model.json")
print("\nSaved XGBoost model to model.pkl and model.json successfully!")
