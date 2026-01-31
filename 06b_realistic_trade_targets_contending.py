import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------
# Paths
# -----------------------
BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
OUT = BASE / "outputs" / "trade_targets"
OUT.mkdir(parents=True, exist_ok=True)

BR = RAW / "BR Baseball Data 2021-2025.xlsx"
SAV_BAT = RAW / "Savant Batter 2021-2025.csv"
SAV_PIT = RAW / "Savant Pitcher 2021-2025.csv"

# -----------------------
# Load 2025 data
# -----------------------
bat = pd.read_excel(BR, sheet_name="BATTER2025")
pit = pd.read_excel(BR, sheet_name="PITCHER2025")

sav_b = pd.read_csv(SAV_BAT)
sav_p = pd.read_csv(SAV_PIT)

sav_b = sav_b[sav_b["year"] == 2025]
sav_p = sav_p[sav_p["year"] == 2025]

# -----------------------
# Name cleaning
# -----------------------
def clean_br(x):
    return str(x).replace("*", "").replace("#", "").lower().strip()

def clean_sav(x):
    last, first = str(x).split(",")
    return f"{first.strip()} {last.strip()}".lower()

bat["name"] = bat["Player"].map(clean_br)
pit["name"] = pit["Player"].map(clean_br)
sav_b["name"] = sav_b["last_name, first_name"].map(clean_sav)
sav_p["name"] = sav_p["last_name, first_name"].map(clean_sav)

# -----------------------
# Merge
# -----------------------
bat = bat.merge(
    sav_b[["name", "xwoba", "xslg", "k_percent", "bb_percent"]],
    on="name", how="left"
)

pit = pit.merge(
    sav_p[["name", "whiff_percent", "k_percent", "bb_percent", "xwoba"]],
    on="name", how="left"
)

# -----------------------
# Exclude ARI + elite teams
# -----------------------
CONTENDERS = ["LAD", "ATL", "NYY", "HOU", "PHI", "BAL", "TBR"]

bat = bat[(bat["Team"] != "ARI") & (~bat["Team"].isin(CONTENDERS))]
pit = pit[(pit["Team"] != "ARI") & (~pit["Team"].isin(CONTENDERS))]

# -----------------------
# RELIEVER TARGETS
# -----------------------
rel = pit[(pit["GS"] <= 3) & (pit["IP"] >= 25)]

# Exclude elite relievers
rel = rel[rel["WAR"] <= 2.0]

rel_targets = rel.sort_values(
    ["whiff_percent", "WAR"], ascending=[False, True]
).head(12)

rel_targets.to_csv(OUT / "realistic_reliever_targets_contending.csv", index=False)

# -----------------------
# BAT TARGETS
# -----------------------
bats = bat[
    (bat["PA"] >= 250) &
    (bat["PA"] <= 500) &
    (bat["WAR"] <= 3.5)
]

# Avoid stars, prefer underlying quality
bats = bats.sort_values(
    ["xwoba", "xslg"], ascending=False
).head(12)

bats.to_csv(OUT / "realistic_batter_targets_contending.csv", index=False)

print("✅ Step 6B complete — realistic contending targets saved")
print("Relievers:", OUT / "realistic_reliever_targets_contending.csv")
print("Batters:", OUT / "realistic_batter_targets_contending.csv")
