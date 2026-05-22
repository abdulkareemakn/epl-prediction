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

matches = pd.read_csv("data/Matches.csv", parse_dates=["MatchDate"], low_memory=False)

# ── 2. Filter to EPL (top-flight England only) ────────────────────────────────
epl = matches[matches["Division"] == "E0"].copy()

# Fix Nottingham Forest Team Name. Obtained after first run.

TEAM_NAME_MAP = {
    "Nottm Forest": "Nott'm Forest",
}
epl["HomeTeam"] = epl["HomeTeam"].replace(TEAM_NAME_MAP)
epl["AwayTeam"] = epl["AwayTeam"].replace(TEAM_NAME_MAP)

epl["Season"] = epl["MatchDate"].apply(
    lambda x: f"{x.year}/{x.year + 1}" if x.month >= 8 else f"{x.year - 1}/{x.year}"
)

epl = epl[~epl["Season"].isin(EXCLUDED_SEASONS)]

epl["EloDifference"] = epl["HomeElo"] - epl["AwayElo"]
epl["Form3Difference"] = epl["Form3Home"] - epl["Form3Away"]
epl["Form5Difference"] = epl["Form5Home"] - epl["Form5Away"]

# Normalize implied probabilities — removes bookmaker margin, sums to exactly 1.0
raw_implied = (1 / epl["OddHome"]) + (1 / epl["OddDraw"]) + (1 / epl["OddAway"])
epl["NormProbHome"] = (1 / epl["OddHome"]) / raw_implied
epl["NormProbDraw"] = (1 / epl["OddDraw"]) / raw_implied
epl["NormProbAway"] = (1 / epl["OddAway"]) / raw_implied

train = epl[epl["Season"] != VALIDATION_SEASON][COLUMNS].copy()
val = epl[epl["Season"] == VALIDATION_SEASON][COLUMNS].copy()

print(
    f"Training   : {len(train):,} matches  "
    f"({train['MatchDate'].min().date()} → {train['MatchDate'].max().date()})"
)
print(
    f"Validation : {len(val):,} matches  "
    f"({val['MatchDate'].min().date()} → {val['MatchDate'].max().date()})"
)
print(f"Columns    : {COLUMNS}")

train.to_csv("outputs/training.csv", index=False)
val.to_csv("outputs/validation.csv", index=False)

print("\nPreprocessing complete. Files written to outputs/")
