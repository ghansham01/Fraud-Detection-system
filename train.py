import joblib
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import classification_report, roc_auc_score, f1_score

from pipeline.data_pipeline import run_pipeline

def get_model(y_train):
    negative = int((y_train == 0).sum())
    positive = int((y_train == 1).sum())
    scale_pos_weight = max(1.0, np.sqrt(negative / positive))

    return {
        "Logistic Regression": CalibratedClassifierCV(
            estimator=LogisticRegression(
                max_iter=2000,
                C=0.1,
                class_weight={0: 1, 1: 12},
                random_state=42,
            ),
            method="sigmoid",
            cv=3,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8,
            min_samples_leaf=20,
            class_weight={0: 1, 1: 12},
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            min_samples_leaf=5,
            class_weight={0: 1, 1: 12},
            n_jobs=1,
            random_state=42,
        ),
        "XGBoost": XGBClassifier(
            eval_metric="logloss",
            scale_pos_weight=scale_pos_weight,
            max_depth=4,
            learning_rate=0.08,
            n_estimators=150,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        ),
    }


def evealuateModel(name, model, X_test, y_test):
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    f1  = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)


    print(f"\n{'='*50}")
    print(f"{name}")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {auc:.4f}")

    return {"model": name, "f1": f1, "auc": auc, "object": model}


def plot_comparison(results):
    names = [r["model"] for r in results]
    f1s   = [r["f1"]    for r in results]
    aucs  = [r["auc"]   for r in results]

    x = range(len(names))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(x, f1s,  color=["#5DCAA5","#7F77DD","#D85A30","#378ADD"])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=15)
    axes[0].set_title("F1 Score Comparison")
    axes[0].set_ylim(0, 1)

    axes[1].bar(x, aucs, color=["#5DCAA5","#7F77DD","#D85A30","#378ADD"])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=15)
    axes[1].set_title("ROC-AUC Comparison")
    axes[1].set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig("models/model_comparison.png")
    print("\nComparison chart saved to models/model_comparison.png")


def train_all():
    # Run data pipeline
    X_train, X_test, y_train, y_test = run_pipeline()

    models  = get_model(y_train)
    results = []

    # train different-2 models 
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        result = evealuateModel(name, model, X_test, y_test)
        results.append(result)

    # Pick beat model by F1 score
    best = max(results, key=lambda r: r["f1"])
    print(f"\nBest model: {best['model']} (F1={best['f1']:.4f}, AUC={best['auc']:.4f})")

    # Save best model
    joblib.dump(best["object"], "models/fraud_model.pkl")
    print(f"Best model saved to models/fraud_model.pkl")

    # Save all models individually too
    for result in results:
        safe_name = result["model"].lower().replace(" ", "_")
        joblib.dump(result["object"], f"models/{safe_name}.pkl")


    plot_comparison(results)
    return results

if __name__ == "__main__":
    train_all()
