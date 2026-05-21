import os
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────────────
CAT = ["HomeTeam", "AwayTeam"]

NUM_BASE = [
    "HomeElo",
    "AwayElo",
    "EloDifference",
    "Form3Home",
    "Form3Away",
    "Form3Difference",
    "Form5Home",
    "Form5Away",
    "Form5Difference",
]
NUM_ODDS = ["NormProbHome", "NormProbDraw", "NormProbAway"]

FEATURE_SETS = {
    "no_odds": CAT + NUM_BASE,
    "with_odds": CAT + NUM_BASE + NUM_ODDS,
}
NUM_BY_SET = {
    "no_odds": NUM_BASE,
    "with_odds": NUM_BASE + NUM_ODDS,
}

# ── 1. Load ───────────────────────────────────────────────────────────────────
train = pd.read_csv("outputs/training.csv", parse_dates=["MatchDate"])
val = pd.read_csv("outputs/validation.csv", parse_dates=["MatchDate"])

print(f"Training samples  : {len(train):,}")
print(f"Validation samples: {len(val):,}")
print(f"Training class distribution:\n{train['FTResult'].value_counts()}")
print(f"\nValidation class distribution:\n{val['FTResult'].value_counts()}")

# print("Train NaNs:\n", train[NUM_BASE].isnull().sum())
# print("Val NaNs:\n", val[NUM_BASE].isnull().sum())

# val[val[["HomeElo", "AwayElo"]].isnull().any(axis=1)][
#     ["MatchDate", "HomeTeam", "AwayTeam", "HomeElo", "AwayElo"]
# ]

# raise ValueError("Stop")


# ── 2. Encode target ──────────────────────────────────────────────────────────
# LabelEncoder maps alphabetically: A → 0, D → 1, H → 2
le = LabelEncoder()
y_train = le.fit_transform(train["FTResult"])
y_val = le.transform(val["FTResult"])

print(f"\nLabel encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")


# ── 3. Preprocessors ──────────────────────────────────────────────────────────
def make_lr_preprocessor(num_features):
    """OHE (drop='first') + impute + scale — for Logistic Regression."""
    return ColumnTransformer(
        [
            (
                "ohe",
                OneHotEncoder(
                    handle_unknown="ignore", drop="first", sparse_output=False
                ),
                CAT,
            ),
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_features,
            ),
        ]
    )


def make_tree_preprocessor(num_features):
    """OHE + impute — for Random Forest and XGBoost."""
    return ColumnTransformer(
        [
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
            ("num", SimpleImputer(strategy="median"), num_features),
        ]
    )


# ── 4. Pipelines ──────────────────────────────────────────────────────────────
def build_pipelines(num_features):
    return {
        "logistic_regression": Pipeline(
            [
                ("pre", make_lr_preprocessor(num_features)),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=1000,
                        C=1.0,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("pre", make_tree_preprocessor(num_features)),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=5,
                        n_jobs=-1,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "xgboost": Pipeline(
            [
                ("pre", make_tree_preprocessor(num_features)),
                (
                    "clf",
                    XGBClassifier(
                        n_estimators=300,
                        max_depth=4,
                        learning_rate=0.05,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        objective="multi:softprob",
                        num_class=3,
                        eval_metric="mlogloss",
                        n_jobs=-1,
                        random_state=42,
                        verbosity=0,
                    ),
                ),
            ]
        ),
    }


# ── 5. Evaluate one model ─────────────────────────────────────────────────────
def evaluate(name, pipeline, X_train, y_train, X_val, y_val, le):
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_val)
    y_prob = pipeline.predict_proba(X_val)

    print(f"\n{'═' * 62}")
    print(f"  {name}")
    print(f"{'═' * 62}")
    print(f"  Accuracy : {accuracy_score(y_val, y_pred):.4f}")
    print(f"  Macro F1 : {f1_score(y_val, y_pred, average='macro'):.4f}")
    print(f"  Log-Loss : {log_loss(y_val, y_prob):.4f}")
    print()
    print(classification_report(y_val, y_pred, target_names=le.classes_))
    print("  Confusion matrix  (rows = actual, cols = predicted)")
    print(f"  Classes : {list(le.classes_)}")
    print(confusion_matrix(y_val, y_pred))

    return pipeline


# ── 6. Baselines ──────────────────────────────────────────────────────────────
def run_baselines(val, y_val, le):
    print(f"\n\n{'#' * 62}")
    print("  BASELINES")
    print(f"{'#' * 62}")

    # Baseline 1: Always predict Home Win
    home_label = le.transform(["H"])[0]
    always_home = np.full(len(y_val), home_label)
    print(f"\n  [Always Home Win]")
    print(f"  Accuracy : {accuracy_score(y_val, always_home):.4f}")
    print(
        f"  Macro F1 : {f1_score(y_val, always_home, average='macro', zero_division=0):.4f}"
    )

    # Baseline 2: Bookmaker best probability
    # Class order: A=0, D=1, H=2  →  prob columns must be [NormProbAway, NormProbDraw, NormProbHome]
    bookie_prob = val[["NormProbAway", "NormProbDraw", "NormProbHome"]].values
    bookie_pred = np.argmax(bookie_prob, axis=1)
    print(f"\n  [Bookmaker Best Probability]")
    print(f"  Accuracy : {accuracy_score(y_val, bookie_pred):.4f}")
    print(
        f"  Macro F1 : {f1_score(y_val, bookie_pred, average='macro', zero_division=0):.4f}"
    )
    print(f"  Log-Loss : {log_loss(y_val, bookie_prob):.4f}")
    print()
    print(classification_report(y_val, bookie_pred, target_names=le.classes_))


# ── 7. Main training loop ─────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
trained = {}

for set_name, features in FEATURE_SETS.items():
    print(f"\n\n{'#' * 62}")
    print(f"  FEATURE SET: {set_name.upper()}")
    print(f"{'#' * 62}")

    X_train = train[features]
    X_val = val[features]
    num = NUM_BY_SET[set_name]

    for model_name, pipeline in build_pipelines(num).items():
        label = f"{model_name}  [{set_name}]"
        fitted = evaluate(label, pipeline, X_train, y_train, X_val, y_val, le)
        trained[f"{model_name}_{set_name}"] = fitted

# ── 8. Baselines ──────────────────────────────────────────────────────────────
run_baselines(val, y_val, le)

# ── 9. Save artifacts ─────────────────────────────────────────────────────────
joblib.dump(le, "models/label_encoder.pkl")
for key, pipeline in trained.items():
    joblib.dump(pipeline, f"models/{key}.pkl")

print(f"\n\nSaved {len(trained)} pipelines + label encoder → models/")
print("Artifacts:")
for key in trained:
    print(f"  models/{key}.pkl")
print("  models/label_encoder.pkl")
