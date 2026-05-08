import pandas as pd
import numpy as np


matches = pd.read_csv("data/Matches.csv", parse_dates=["MatchDate"], low_memory=False)

epl = matches[matches["Division"] == "E0"].copy()

epl["Season"] = epl["MatchDate"].apply(
    lambda x: f"{x.year}/{x.year + 1}" if x.month >= 8 else f"{x.year - 1}/{x.year}"
)


epl = epl[~epl["Season"].isin(["2000/2001", "2001/2002"])]


print(epl["Season"].value_counts().sort_index())

print(epl.shape)

epl["EloDifference"] = epl["HomeElo"] - epl["AwayElo"]
epl["Form3Difference"] = epl["Form3Home"] - epl["Form3Away"]
epl["Form5Difference"] = epl["Form5Home"] - epl["Form5Away"]
epl["ImpliedProbHome"] = 1 / epl["OddHome"]
epl["ImpliedProbDraw"] = 1 / epl["OddDraw"]
epl["ImpliedProbAway"] = 1 / epl["OddAway"]

epl_final = epl[
    [
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
        "OddHome",
        "OddDraw",
        "OddAway",
        "ImpliedProbHome",
        "ImpliedProbDraw",
        "ImpliedProbAway",
        "FTResult",
    ]
].copy()

epl_final.to_csv("outputs/processed_epl_data.csv", index=False)

epl_validation = epl[epl["Season"] == "2024/2025"].copy()
epl_validation_final = epl_validation[
    [
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
        "OddHome",
        "OddDraw",
        "OddAway",
        "ImpliedProbHome",
        "ImpliedProbDraw",
        "ImpliedProbAway",
        "FTResult",
    ]
]

epl_validation_final.to_csv("outputs/validation_epl_data.csv", index=False)

# print(epl.head(10))
# print(epl)

# print(epl.columns)
