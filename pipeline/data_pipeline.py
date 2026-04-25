import os

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_data(path="data/creditcard.csv"):
    df = pd.read_csv(path)
    print(f"Dataset shape: {df.shape}")
    print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].mean() * 100:.2f}%)")
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
    scaler = StandardScaler()
    df[["Amount_scaled", "Time_scaled"]] = scaler.fit_transform(df[["Amount", "Time"]])
    df = df.drop(columns=["Amount", "Time"])
    return df, scaler


def split_data(df):
    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")
    print(f"Fraud in train: {y_train.sum()}, Fraud in test: {y_test.sum()}")
    return X_train, X_test, y_train, y_test


def save_artifacts(scaler, feature_cols):
    os.makedirs("models", exist_ok=True)

    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(feature_cols, "models/feature_cols.pkl")

    print("Scaler saved -> models/scaler.pkl")
    print("Feature cols saved -> models/feature_cols.pkl")
    print(f"Features: {feature_cols}")


def run_pipeline():
    df = load_data()
    df = clean_data(df)
    df, scaler = engineer_features(df)

    X_train, X_test, y_train, y_test = split_data(df)

    save_artifacts(scaler, list(X_train.columns))

    return X_train, X_test, y_train, y_test
