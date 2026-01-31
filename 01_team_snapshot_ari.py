import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

TEAM = "ARI"
YEARS = [2021, 2022, 2023, 2024, 2025]

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data" / "processed"

BATTERS_FILE = DATA_DIR / "ARI_BR_batters_2021_2025.csv"
PITCHERS_FILE = DATA_DIR / "ARI_BR_pitchers_2021_2025.csv"

# Safety check
for p in [BATTERS_FILE, PITCHERS_FILE]:
    if not p.exists():
        raise FileNotFoundError(f"Missing required file: {p}")

OUT_DIR = SCRIPT_DIR / "outputs" / "team_snapshot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load
# -----------------------------
bat = pd.read_csv(BATTERS_FILE)
pit = pd.read_csv(PITCHERS_FILE)

# Keep only years of interest (safety)
bat = bat[bat["Year"].isin(YEARS)].copy()
pit = pit[pit["Year"].isin(YEARS)].copy()

# -----------------------------
# Helper: detect useful columns safely
# -----------------------------
def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# Common column name variations in BR exports
WAR_COL_BAT = pick_col(bat, ["WAR", "bWAR", "WAR_bat"])
WAR_COL_PIT = pick_col(pit, ["WAR", "pWAR", "WAR_pit"])
AGE_COL_BAT = pick_col(bat, ["Age", "age"])
AGE_COL_PIT = pick_col(pit, ["Age", "age"])
PA_COL = pick_col(bat, ["PA", "Batters Faced", "BF"])  # usually PA exists
IP_COL = pick_col(pit, ["IP", "IPouts"])              # usually IP exists
GS_COL = pick_col(pit, ["GS", "Games Started"])

if WAR_COL_BAT is None or WAR_COL_PIT is None:
    raise ValueError("Could not find WAR columns in BR files. Check column names.")

# -----------------------------
# 1) Year-by-year team totals
# -----------------------------
# Batting totals
bat_year = (
    bat.groupby("Year")
       .agg(
           team_WAR=(WAR_COL_BAT, "sum"),
           total_PA=(PA_COL, "sum") if PA_COL else (WAR_COL_BAT, "size"),
           avg_age=(AGE_COL_BAT, "mean") if AGE_COL_BAT else (WAR_COL_BAT, "size"),
           n_batters=("Player", "nunique") if "Player" in bat.columns else (WAR_COL_BAT, "size"),
       )
       .reset_index()
)
# Pitching totals
pit_year = (
    pit.groupby("Year")
       .agg(
           team_WAR=(WAR_COL_PIT, "sum"),
           total_IP=(IP_COL, "sum") if IP_COL else (WAR_COL_PIT, "size"),
           avg_age=(AGE_COL_PIT, "mean") if AGE_COL_PIT else (WAR_COL_PIT, "size"),
           n_pitchers=("Player", "nunique") if "Player" in pit.columns else (WAR_COL_PIT, "size"),
       )
       .reset_index()
)

bat_year.to_csv(OUT_DIR / "ari_batting_team_totals_by_year.csv", index=False)
pit_year.to_csv(OUT_DIR / "ari_pitching_team_totals_by_year.csv", index=False)

# -----------------------------
# 2) Top contributors by WAR
# -----------------------------
top_bat_by_year = (
    bat.groupby(["Year", "Player"])[WAR_COL_BAT].sum().reset_index()
       .sort_values(["Year", WAR_COL_BAT], ascending=[True, False])
       .groupby("Year")
       .head(10)
)
top_pit_by_year = (
    pit.groupby(["Year", "Player"])[WAR_COL_PIT].sum().reset_index()
       .sort_values(["Year", WAR_COL_PIT], ascending=[True, False])
       .groupby("Year")
       .head(10)
)

top_bat_by_year.to_csv(OUT_DIR / "ari_top10_batters_by_WAR_each_year.csv", index=False)
top_pit_by_year.to_csv(OUT_DIR / "ari_top10_pitchers_by_WAR_each_year.csv", index=False)

# Overall 2021–2025 leaders
bat_overall = (
    bat.groupby("Player")[WAR_COL_BAT].sum().reset_index()
       .sort_values(WAR_COL_BAT, ascending=False)
)
pit_overall = (
    pit.groupby("Player")[WAR_COL_PIT].sum().reset_index()
       .sort_values(WAR_COL_PIT, ascending=False)
)

bat_overall.head(20).to_csv(OUT_DIR / "ari_top20_batters_WAR_2021_2025.csv", index=False)
pit_overall.head(20).to_csv(OUT_DIR / "ari_top20_pitchers_WAR_2021_2025.csv", index=False)

# -----------------------------
# 3) Pitching roles: starter vs reliever (simple rule)
# -----------------------------
# Rule: Starter if GS / G >= 0.5 (or GS >= 10 if G missing)
G_COL = pick_col(pit, ["G", "Games"])
if GS_COL is not None:
    tmp = pit.copy()
    if G_COL is not None:
        tmp["starter_flag"] = (tmp[GS_COL] / tmp[G_COL]).fillna(0) >= 0.5
    else:
        tmp["starter_flag"] = tmp[GS_COL].fillna(0) >= 10

    role_year = (
        tmp.groupby(["Year", "starter_flag"])
           .agg(
               pitchers=("Player", "nunique"),
               total_WAR=(WAR_COL_PIT, "sum"),
               total_IP=(IP_COL, "sum") if IP_COL else (WAR_COL_PIT, "size"),
           )
           .reset_index()
    )
    role_year["role"] = role_year["starter_flag"].map({True: "Starter", False: "Reliever"})
    role_year.drop(columns=["starter_flag"], inplace=True)

    role_year.to_csv(OUT_DIR / "ari_pitching_roles_by_year.csv", index=False)

# -----------------------------
# 4) Age profile
# -----------------------------
if AGE_COL_BAT:
    bat_age = bat[["Year", "Player", AGE_COL_BAT]].dropna()
    bat_age.to_csv(OUT_DIR / "ari_batters_age_player_year.csv", index=False)

if AGE_COL_PIT:
    pit_age = pit[["Year", "Player", AGE_COL_PIT]].dropna()
    pit_age.to_csv(OUT_DIR / "ari_pitchers_age_player_year.csv", index=False)

# -----------------------------
# 5) Plots for slides (saved as PNG)
# -----------------------------
# Team WAR trend (bat + pit)
plt.figure()
plt.plot(bat_year["Year"], bat_year["team_WAR"], marker="o")
plt.title("Arizona Diamondbacks — Batting WAR (Team Total) by Year")
plt.xlabel("Year")
plt.ylabel("Team Batting WAR")
plt.xticks(YEARS)
plt.tight_layout()
plt.savefig(OUT_DIR / "plot_batting_WAR_by_year.png", dpi=200)
plt.close()

plt.figure()
plt.plot(pit_year["Year"], pit_year["team_WAR"], marker="o")
plt.title("Arizona Diamondbacks — Pitching WAR (Team Total) by Year")
plt.xlabel("Year")
plt.ylabel("Team Pitching WAR")
plt.xticks(YEARS)
plt.tight_layout()
plt.savefig(OUT_DIR / "plot_pitching_WAR_by_year.png", dpi=200)
plt.close()

# 2025 top 10 batters WAR bar
if 2025 in bat["Year"].unique():
    top_2025_bat = (bat[bat["Year"] == 2025]
                    .groupby("Player")[WAR_COL_BAT].sum()
                    .sort_values(ascending=False)
                    .head(10))
    plt.figure(figsize=(8, 4))
    top_2025_bat.sort_values().plot(kind="barh")
    plt.title("Top 10 ARI Batters by WAR (2025)")
    plt.xlabel("WAR")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "plot_top10_batters_WAR_2025.png", dpi=200)
    plt.close()

# 2025 top 10 pitchers WAR bar
if 2025 in pit["Year"].unique():
    top_2025_pit = (pit[pit["Year"] == 2025]
                    .groupby("Player")[WAR_COL_PIT].sum()
                    .sort_values(ascending=False)
                    .head(10))
    plt.figure(figsize=(8, 4))
    top_2025_pit.sort_values().plot(kind="barh")
    plt.title("Top 10 ARI Pitchers by WAR (2025)")
    plt.xlabel("WAR")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "plot_top10_pitchers_WAR_2025.png", dpi=200)
    plt.close()

print(f"✅ Team snapshot outputs saved to: {OUT_DIR}")
print("Next: merge Savant features + build evaluation model.")
