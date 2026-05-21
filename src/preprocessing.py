import pandas as pd

# ── Configuration ─────────────────────────────────────────────────────────────
VALIDATION_SEASON = "2024/2025"
EXCLUDED_SEASONS = ["2000/2001", "2001/2002"]

COLUMNS = [
    "MatchDate",
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
    "FTResult",
]

# ── 1. Load ───────────────────────────────────────────────────────────────────
matches = pd.read_csv("data/Matches.csv", parse_dates=["MatchDate"], low_memory=False)

# ── 2. Filter to EPL (top-flight England only) ────────────────────────────────
epl = matches[matches["Division"] == "E0"].copy()

# Fix Nottingham Forest Team Name. Obtained after first run.

TEAM_NAME_MAP = {
    "Nottm Forest": "Nott'm Forest",
}
epl["HomeTeam"] = epl["HomeTeam"].replace(TEAM_NAME_MAP)
epl["AwayTeam"] = epl["AwayTeam"].replace(TEAM_NAME_MAP)

# ── 3. Derive season label ────────────────────────────────────────────────────
epl["Season"] = epl["MatchDate"].apply(
    lambda x: f"{x.year}/{x.year + 1}" if x.month >= 8 else f"{x.year - 1}/{x.year}"
)

# ── 4. Drop seasons with insufficient form/Elo history ────────────────────────
epl = epl[~epl["Season"].isin(EXCLUDED_SEASONS)]

# ── 5. Compute derived features ───────────────────────────────────────────────
epl["EloDifference"] = epl["HomeElo"] - epl["AwayElo"]
epl["Form3Difference"] = epl["Form3Home"] - epl["Form3Away"]
epl["Form5Difference"] = epl["Form5Home"] - epl["Form5Away"]

# Normalize implied probabilities — removes bookmaker margin, sums to exactly 1.0
raw_implied = (1 / epl["OddHome"]) + (1 / epl["OddDraw"]) + (1 / epl["OddAway"])
epl["NormProbHome"] = (1 / epl["OddHome"]) / raw_implied
epl["NormProbDraw"] = (1 / epl["OddDraw"]) / raw_implied
epl["NormProbAway"] = (1 / epl["OddAway"]) / raw_implied

# ── 6. Split (Season column used here, then discarded via COLUMNS) ─────────────
train = epl[epl["Season"] != VALIDATION_SEASON][COLUMNS].copy()
val = epl[epl["Season"] == VALIDATION_SEASON][COLUMNS].copy()

# ── 7. Sanity checks ──────────────────────────────────────────────────────────
assert (
    (train["NormProbHome"] + train["NormProbDraw"] + train["NormProbAway"])
    .round(6)
    .eq(1.0)
    .all()
), "NormProbs don't sum to 1 in training set"

assert (
    (val["NormProbHome"] + val["NormProbDraw"] + val["NormProbAway"])
    .round(6)
    .eq(1.0)
    .all()
), "NormProbs don't sum to 1 in validation set"

assert train["MatchDate"].max() < val["MatchDate"].min(), (
    "Temporal leakage: training and validation dates overlap"
)

# ── 8. Summary ────────────────────────────────────────────────────────────────
print(
    f"Training   : {len(train):,} matches  "
    f"({train['MatchDate'].min().date()} → {train['MatchDate'].max().date()})"
)
print(
    f"Validation : {len(val):,} matches  "
    f"({val['MatchDate'].min().date()} → {val['MatchDate'].max().date()})"
)
print(f"Columns    : {COLUMNS}")

# ── 9. Save ───────────────────────────────────────────────────────────────────
train.to_csv("outputs/training.csv", index=False)
val.to_csv("outputs/validation.csv", index=False)
print("\nPreprocessing complete. Files written to outputs/")


# import pandas as pd
# import numpy as np


# matches = pd.read_csv("data/Matches.csv", parse_dates=["MatchDate"], low_memory=False)

# initial_shape = [
#     "Season",
#     "MatchDate",
#     "HomeTeam",
#     "AwayTeam",
#     "HomeElo",
#     "AwayElo",
#     "EloDifference",
#     "Form3Home",
#     "Form3Away",
#     "Form3Difference",
#     "Form5Home",
#     "Form5Away",
#     "Form5Difference",
#     # "OddHome",
#     # "OddDraw",
#     # "OddAway",
#     # "ImpliedProbHome",
#     # "ImpliedProbDraw",
#     # "ImpliedProbAway",
#     "FTResult",
# ]

# final_shape = [
#     "MatchDate",
#     "HomeTeam",
#     "AwayTeam",
#     "HomeElo",
#     "AwayElo",
#     "EloDifference",
#     "Form3Home",
#     "Form3Away",
#     "Form3Difference",
#     "Form5Home",
#     "Form5Away",
#     "Form5Difference",
#     "NormProbHome",
#     "NormProbDraw",
#     "NormProbAway",
#     # "OddHome",
#     # "OddDraw",
#     # "OddAway",
#     # "ImpliedProbHome",
#     # "ImpliedProbDraw",
#     # "ImpliedProbAway",
#     "FTResult",
# ]

# epl = matches[matches["Division"] == "E0"].copy()

# epl["Season"] = epl["MatchDate"].apply(
#     lambda x: f"{x.year}/{x.year + 1}" if x.month >= 8 else f"{x.year - 1}/{x.year}"
# )


# epl = epl[~epl["Season"].isin(["2000/2001", "2001/2002"])]


# # print(epl["Season"].value_counts().sort_index())

# # print(epl.shape)

# epl["EloDifference"] = epl["HomeElo"] - epl["AwayElo"]
# epl["Form3Difference"] = epl["Form3Home"] - epl["Form3Away"]
# epl["Form5Difference"] = epl["Form5Home"] - epl["Form5Away"]
# epl["ImpliedProbHome"] = 1 / epl["OddHome"]
# epl["ImpliedProbDraw"] = 1 / epl["OddDraw"]
# epl["ImpliedProbAway"] = 1 / epl["OddAway"]

# raw_sum = epl["ImpliedProbHome"] + epl["ImpliedProbDraw"] + epl["ImpliedProbAway"]
# epl["NormProbHome"] = epl["ImpliedProbHome"] / raw_sum
# epl["NormProbDraw"] = epl["ImpliedProbDraw"] / raw_sum
# epl["NormProbAway"] = epl["ImpliedProbAway"] / raw_sum

# epl.drop(
#     columns=[
#         "OddHome",
#         "OddDraw",
#         "OddAway",
#         "ImpliedProbHome",
#         "ImpliedProbDraw",
#         "ImpliedProbAway",
#     ],
#     inplace=True,
# )

# epl_final_shape = epl[initial_shape].copy()

# epl_final_shape = epl_final_shape[~epl_final_shape["Season"].isin(["2024/2025"])]
# epl_fianal_shape_validation = epl_final_shape[final_shape]
# # epl_final_shape.to_csv("outputs/processed_epl_data.csv", index=False)

# epl_validation = epl[epl["Season"] == "2024/2025"].copy()
# epl_validation_final = epl_validation[final_shape]

# epl_validation_final.to_csv("outputs/validation.csv", index=False)
# epl_fianal_shape_validation.to_csv("outputs/training.csv", index=False)

# # print(epl.head(10))
# # print(epl)

# # print(epl.columns)
