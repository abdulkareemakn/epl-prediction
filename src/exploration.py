import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_DIR = Path("data")

matches = pd.read_csv(
    DATA_DIR / "Matches.csv", parse_dates=["MatchDate"], low_memory=False
)
elo = pd.read_csv(DATA_DIR / "EloRatings.csv", parse_dates=["date"])

epl = matches[matches["Division"] == "E0"].copy()

print(f"Matches Shape: {matches.shape}")
print(f"Ratings Shape: {elo.shape}")

print(matches.columns)
print(elo.columns)

matches["Division"].value_counts().head(10)

epl["FTResult"].value_counts()

epl[
    [
        "HomeElo",
        "AwayElo",
        "Form3Home",
        "Form3Away",
        "Form5Home",
        "Form5Away",
        "OddHome",
        "OddDraw",
        "OddAway",
    ]
].isnull().sum()

epl[epl["OddHome"].isnull()]["MatchDate"].describe()

epl["MatchDate"].dt.month

epl["MatchDate"].dt.year

epl["Season"] = epl["MatchDate"].apply(
    lambda x: f"{x.year}/{x.year + 1}" if x.month >= 8 else f"{x.year - 1}/{x.year}"
)

epl["Season"].value_counts().sort_index()

# print(f"{matches.dtypes}")
