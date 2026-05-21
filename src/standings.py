import joblib
import pandas as pd
from scipy.stats import spearmanr

# ── 1. Load ───────────────────────────────────────────────────────────────────
val = pd.read_csv("outputs/validation.csv", parse_dates=["MatchDate"])
le = joblib.load("models/label_encoder.pkl")
model = joblib.load("models/xgboost_with_odds.pkl")

FEATURES = [
    "HomeTeam",
    "AwayTeam",
    "HomeElo",
    "AwayElo",
    "EloDifference",
    "Form3Home",
    "Form3Away",
    "Form3Difference",
    "Form5Home",
    "Form5Away",
    "Form5Difference",
    "NormProbHome",
    "NormProbDraw",
    "NormProbAway",
]

# ── 2. Predict ────────────────────────────────────────────────────────────────
X_val = val[FEATURES]
y_pred_enc = model.predict(X_val)
y_pred_labels = le.inverse_transform(y_pred_enc)  # back to 'H' / 'D' / 'A'

val = val.copy()
val["PredictedResult"] = y_pred_labels


# ── 3. Points table builder ───────────────────────────────────────────────────
def compute_standings(df, result_col, label="Standings"):
    teams = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
    stats = {t: {"P": 0, "W": 0, "D": 0, "L": 0, "Pts": 0} for t in teams}

    for _, row in df.iterrows():
        home = row["HomeTeam"]
        away = row["AwayTeam"]
        result = row[result_col]

        stats[home]["P"] += 1
        stats[away]["P"] += 1

        if result == "H":
            stats[home]["W"] += 1
            stats[home]["Pts"] += 3
            stats[away]["L"] += 1
        elif result == "D":
            stats[home]["D"] += 1
            stats[home]["Pts"] += 1
            stats[away]["D"] += 1
            stats[away]["Pts"] += 1
        elif result == "A":
            stats[away]["W"] += 1
            stats[away]["Pts"] += 3
            stats[home]["L"] += 1

    table = (
        pd.DataFrame(stats)
        .T.reset_index()
        .rename(columns={"index": "Team"})
        .sort_values("Pts", ascending=False)
        .reset_index(drop=True)
    )
    table.index += 1
    table.index.name = "Pos"
    return table


# ── 4. Build both tables ──────────────────────────────────────────────────────
actual_table = compute_standings(val, "FTResult", "Actual")
predicted_table = compute_standings(val, "PredictedResult", "Predicted")

# ── 5. Spearman rank correlation ──────────────────────────────────────────────
# Align by team using actual table order as reference
teams_in_order = actual_table["Team"].tolist()
pred_order = predicted_table["Team"].tolist()

actual_ranks = list(range(1, len(teams_in_order) + 1))
predicted_ranks = [pred_order.index(t) + 1 for t in teams_in_order]

rho, pvalue = spearmanr(actual_ranks, predicted_ranks)

# ── 6. Side-by-side comparison ────────────────────────────────────────────────
comparison = actual_table[["Team", "Pts"]].copy()
comparison.columns = ["Team", "Actual Pts"]
comparison["Actual Pos"] = comparison.index

pred_pos = {team: pos for pos, team in enumerate(pred_order, start=1)}
pred_pts = predicted_table.set_index("Team")["Pts"].to_dict()

comparison["Pred Pos"] = comparison["Team"].map(pred_pos)
comparison["Pred Pts"] = comparison["Team"].map(pred_pts)
comparison["Pos Diff"] = comparison["Pred Pos"] - comparison["Actual Pos"]
comparison = comparison[
    ["Team", "Actual Pos", "Actual Pts", "Pred Pos", "Pred Pts", "Pos Diff"]
]
comparison = comparison.sort_values("Actual Pos").reset_index(drop=True)

# ── 7. Print ──────────────────────────────────────────────────────────────────
print("=" * 70)
print("  ACTUAL 2024/25 STANDINGS")
print("=" * 70)
print(actual_table[["Team", "P", "W", "D", "L", "Pts"]].to_string())

print("\n")
print("=" * 70)
print("  PREDICTED 2024/25 STANDINGS  (XGBoost + odds)")
print("=" * 70)
print(predicted_table[["Team", "P", "W", "D", "L", "Pts"]].to_string())

print("\n")
print("=" * 70)
print("  COMPARISON  (sorted by actual position)")
print("=" * 70)
print(comparison.to_string(index=False))

print(f"\n  Spearman rank correlation : {rho:.4f}")
print(f"  p-value                   : {pvalue:.4f}")

if rho >= 0.9:
    verdict = "Excellent — near-perfect ranking agreement"
elif rho >= 0.75:
    verdict = "Strong — model captures the season's shape well"
elif rho >= 0.5:
    verdict = "Moderate — broad structure correct, detail lost"
else:
    verdict = "Weak — model struggles to reproduce season order"

print(f"  Interpretation            : {verdict}")

# ── 8. Save ───────────────────────────────────────────────────────────────────
actual_table.to_csv("outputs/actual_standings.csv")
predicted_table.to_csv("outputs/predicted_standings.csv")
comparison.to_csv("outputs/standings_comparison.csv", index=False)
print("\nStandings written to outputs/")
