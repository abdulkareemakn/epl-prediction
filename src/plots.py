import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.alpha": 0.4,
        "axes.axisbelow": True,
    }
)

# ── Palette ───────────────────────────────────────────────────────────────────
C_NO_ODDS = "#37003c"
C_WITH_ODDS = "#00b894"
C_HOME = "#b2bec3"
C_BOOKIE = "#e17055"

# ── 1. Accuracy Bar Chart ─────────────────────────────────────────────────────
models = ["Logistic\nRegression", "Random\nForest", "XGBoost"]
no_odds = [0.4947, 0.5000, 0.4789]
with_odds = [0.5158, 0.5316, 0.5342]

baseline_home = 0.4079
baseline_bookie = 0.5421

x = np.arange(len(models))
width = 0.32

fig, ax = plt.subplots(figsize=(9, 5.5))

bars1 = ax.bar(
    x - width / 2, no_odds, width, color=C_NO_ODDS, label="No Odds", zorder=3
)
bars2 = ax.bar(
    x + width / 2, with_odds, width, color=C_WITH_ODDS, label="With Odds", zorder=3
)

ax.axhline(
    baseline_home,
    color=C_HOME,
    linewidth=1.6,
    linestyle="--",
    zorder=2,
    label=f"Always Home Win  ({baseline_home:.4f})",
)
ax.axhline(
    baseline_bookie,
    color=C_BOOKIE,
    linewidth=1.6,
    linestyle=":",
    zorder=2,
    label=f"Bookmaker  ({baseline_bookie:.4f})",
)

for bars in (bars1, bars2):
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.003,
            f"{h:.4f}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#2d3436",
        )

ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=9.5)
ax.set_ylim(0.35, 0.60)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.set_ylabel("Accuracy", fontsize=10)
ax.set_title(
    "Prediction Accuracy — All Models vs Baselines\n2024/25 EPL Validation Season (380 matches)",
    fontsize=11,
    fontweight="bold",
    pad=14,
)
ax.legend(fontsize=8.5, framealpha=0.95, loc="lower right")

plt.tight_layout()
plt.savefig("outputs/plot_accuracy.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: outputs/plot_accuracy.png")

# ── 2. Confusion Matrix Grid (2 × 3) ─────────────────────────────────────────
# Rows = feature set, Cols = model
# Values from final run (rows = actual, cols = predicted, order: A D H)

CMS = [
    # No Odds
    np.array([[58, 4, 70], [28, 2, 63], [22, 5, 128]]),  # LR
    np.array([[60, 3, 69], [31, 1, 61], [25, 1, 129]]),  # RF
    np.array([[55, 8, 69], [30, 1, 62], [25, 4, 126]]),  # XGB
    # With Odds
    np.array([[66, 6, 60], [33, 2, 58], [22, 5, 128]]),  # LR
    np.array([[75, 3, 54], [32, 1, 60], [25, 4, 126]]),  # RF
    np.array([[73, 5, 54], [31, 2, 60], [22, 5, 128]]),  # XGB
]

COL_TITLES = ["Logistic Regression", "Random Forest", "XGBoost"]
ROW_TITLES = ["No Odds", "With Odds"]
CLASSES = ["Away", "Draw", "Home"]

fig, axes = plt.subplots(2, 3, figsize=(13, 8.5))
fig.suptitle(
    "Confusion Matrices — Rows: Actual Outcome · Columns: Predicted Outcome",
    fontsize=12,
    fontweight="bold",
    y=1.01,
)

for i, cm in enumerate(CMS):
    row = i // 3
    col = i % 3
    ax = axes[row][col]

    # Normalise by true class (row) to get recall per class
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    # Annotation: percentage on top, raw count below
    annot = np.empty((3, 3), dtype=object)
    for r in range(3):
        for c in range(3):
            annot[r, c] = f"{cm_norm[r, c]:.0%}\n({cm[r, c]})"

    sns.heatmap(
        cm_norm,
        ax=ax,
        annot=annot,
        fmt="",
        cmap="Purples",
        vmin=0,
        vmax=1,
        xticklabels=CLASSES,
        yticklabels=CLASSES,
        linewidths=0.6,
        linecolor="white",
        cbar=False,
        annot_kws={"size": 8.5},
    )

    ax.set_title(
        f"{COL_TITLES[col]}\n[{ROW_TITLES[row]}]",
        fontsize=9.5,
        fontweight="600",
        pad=8,
    )
    ax.set_xlabel("Predicted", fontsize=8.5)
    ax.set_ylabel("Actual", fontsize=8.5)
    ax.tick_params(axis="both", labelsize=8.5)

    # Bold the diagonal (correct predictions)
    for r in range(3):
        ax.add_patch(
            plt.Rectangle(
                (r, r),
                1,
                1,
                fill=False,
                edgecolor="#37003c",
                linewidth=2,
                clip_on=False,
            )
        )

# Row labels on left margin
for row, label in enumerate(ROW_TITLES):
    fig.text(
        0.01,
        0.75 - row * 0.5,
        label,
        va="center",
        ha="left",
        fontsize=11,
        fontweight="bold",
        color="#37003c",
        rotation=90,
    )

plt.tight_layout()
plt.savefig("outputs/plot_confusion.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: outputs/plot_confusion.png")
