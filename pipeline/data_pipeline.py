import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib
import os

def load_data(path="data/creditcard.csv"):
    df = pd.read_csv(path)
    print(f"Dataset shape: {df.shape}")
    print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].mean()*100:.2f}%)")
    return df

def clean_data(df):
    missing = df.isnull().sum()
    if missing.any():
        print(f"Missing values found:\n{missing[missing > 0]}")
        df = df.dropna()
    else:
        print("No missing values found")

    before = len(df)
    df = df.drop_duplicates()
    print(f"Duplicates removed: {before - len(df)}")
    return df

def engineer_features(df):
    # ONE scaler for both Amount and Time together
    scaler = StandardScaler()
    df[["Amount_scaled", "Time_scaled"]] = scaler.fit_transform(df[["Amount", "Time"]])

    # Drop original columns
    df = df.drop(columns=["Amount", "Time"])
    return df, scaler

def split_data(df):
    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")
    print(f"Fraud in train: {y_train.sum()}, Fraud in test: {y_test.sum()}")
    return X_train, X_test, y_train, y_test

def apply_smote(X_train, y_train):
    print(f"Before SMOTE — Legit: {(y_train==0).sum()}, Fraud: {(y_train==1).sum()}")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE  — Legit: {(y_resampled==0).sum()}, Fraud: {(y_resampled==1).sum()}")
    return X_resampled, y_resampled

def save_artifacts(scaler, feature_cols):
    os.makedirs("models", exist_ok=True)

    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(feature_cols, "models/feature_cols.pkl")

    print(f"Scaler saved → models/scaler.pkl")
    print(f"Feature cols saved → models/feature_cols.pkl")
    print(f"Features: {feature_cols}")

def run_pipeline():
    df = load_data()
    df = clean_data(df)
    df, scaler = engineer_features(df)

    X_train, X_test, y_train, y_test = split_data(df)
    X_train_bal, y_train_bal = apply_smote(X_train, y_train)

    # Save scaler + feature column names
    save_artifacts(scaler, list(X_train.columns))

    return X_train_bal, X_test, y_train_bal, y_test