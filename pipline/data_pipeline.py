import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "archive.zip")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "processed")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "scaler.pkl")
RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_data(path: str) -> pd.DataFrame:

    print(f"\n[1/6] Loading data from: {path}")
    df = pd.read_csv(path)

    print(f"      Shape        : {df.shape}")
    print(f"      Columns      : {list(df.columns)}")
    print(f"      Memory usage : {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
    return df


def explore_data(df: pd.DataFrame) -> None:

    print("\n[2/6] Exploring data...")


    counts = df["Class"].value_counts()
    fraud_pct = counts[1] / len(df) * 100

    print(f"      Legit txns   : {counts[0]:,}")
    print(f"      Fraud txns   : {counts[1]:,}")
    print(f"      Fraud rate   : {fraud_pct:.4f}%  ← severe imbalance")

    missing = df.isnull().sum().sum()
    print(f"      Missing vals : {missing}")

    # Amount stats
    print(f"      Amount range : ${df['Amount'].min():.2f} – ${df['Amount'].max():.2f}")
    print(f"      Amount mean  : ${df['Amount'].mean():.2f}")


# ─────────────────────────────────────────
# STEP 3 — Handle Missing Values
# ─────────────────────────────────────────
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
      - Numeric columns  → fill with median (robust to outliers)
      - Drop rows where the target 'Class' is missing
    """
    print("\n[3/6] Handling missing values...")
    before = len(df)

    # Drop rows where label is missing — no label = useless row
    df = df.dropna(subset=["Class"])

    # Fill numeric nulls with column median
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"Filled '{col}' nulls with median={median_val:.4f}")

    after = len(df)
    print(f"Rows before: {before:,}")
    print(f"Rows after: {after:,}")
    return df


# ─────────────────────────────────────────
# STEP 4 — Feature Scaling
# ─────────────────────────────────────────
def scale_features(df: pd.DataFrame, save_scaler: bool = True) -> pd.DataFrame:
    """
    'Amount' and 'Time' are raw — V1-V28 are already PCA-scaled.
    We StandardScale Amount and Time so all features are on the same range.
    The scaler is saved as a .pkl — the API will load this same scaler at prediction time.
    """
    print("\n[4/6] Scaling features (Amount, Time)...")

    scaler = StandardScaler()
    df["Amount"] = scaler.fit_transform(df[["Amount"]])
    df["Time"]   = scaler.fit_transform(df[["Time"]])

    # Drop original unscaled (already replaced above)
    print(f"      Amount scaled: mean={df['Amount'].mean():.4f}, std={df['Amount'].std():.4f}")
    print(f"      Time   scaled: mean={df['Time'].mean():.4f}, std={df['Time'].std():.4f}")

    if save_scaler:
        os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        print(f"      Scaler saved : {SCALER_PATH}")

    return df


# ─────────────────────────────────────────
# STEP 5 — Train / Test Split
# ─────────────────────────────────────────
def split_data(df: pd.DataFrame):
    """
    Split BEFORE applying SMOTE.
    Important: SMOTE should only be applied to training data —
    never to the test set (that would leak synthetic data into evaluation).
    """
    print("\n[5/6] Splitting into train / test sets...")

    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y           # preserves fraud ratio in both splits
    )

    print(f"      X_train : {X_train.shape}")
    print(f"      X_test  : {X_test.shape}")
    print(f"      Fraud in train : {y_train.sum()} ({y_train.mean()*100:.3f}%)")
    print(f"      Fraud in test  : {y_test.sum()} ({y_test.mean()*100:.3f}%)")

    return X_train, X_test, y_train, y_test


# ─────────────────────────────────────────
# STEP 6 — Handle Class Imbalance (SMOTE)
# ─────────────────────────────────────────
def apply_smote(X_train, y_train):
    """
    SMOTE (Synthetic Minority Over-sampling Technique):
    Generates synthetic fraud samples so the model sees a balanced dataset.
    Applied ONLY on train set — test set stays real and untouched.
    """
    print("\n[6/6] Applying SMOTE to training set...")
    print(f"      Before — Legit: {(y_train==0).sum():,}  Fraud: {(y_train==1).sum():,}")

    smote = SMOTE(random_state=RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train.values.ravel())

    print(f"      After  — Legit: {(y_resampled==0).sum():,}  Fraud: {(y_resampled==1).sum():,}")
    print(f"      Total training samples: {len(X_resampled):,}")

    return X_resampled, y_resampled


# ─────────────────────────────────────────
# STEP 7 — Save Processed Data
# ─────────────────────────────────────────
def save_processed(X_train, X_test, y_train, y_test) -> None:
    """Save train/test splits as CSV for use in model training step."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    train_df = X_train.copy()
    train_df["Class"] = y_train.values

    test_df = X_test.copy()
    test_df["Class"] = y_test.values

    train_path = os.path.join(OUTPUT_DIR, "train.csv")
    test_path  = os.path.join(OUTPUT_DIR, "test.csv")

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path,   index=False)

    print(f"\n      Saved train → {train_path}  ({len(train_df):,} rows)")
    print(f"      Saved test  → {test_path}   ({len(test_df):,} rows)")


# ─────────────────────────────────────────
# MAIN — Run full pipeline
# ─────────────────────────────────────────
def run_pipeline():
    print("=" * 50)
    print("  FRAUD DETECTION — DATA PIPELINE")
    print("=" * 50)

    df = load_data(RAW_DATA_PATH)
    explore_data(df)
    df = handle_missing(df)
    df = scale_features(df)
    X_train, X_test, y_train, y_test = split_data(df)
    X_train, y_train = apply_smote(X_train, y_train)
    save_processed(X_train, X_test, y_train, y_test)

    print("\n  Pipeline complete. Ready for model training.")
    print("=" * 50)

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    run_pipeline()