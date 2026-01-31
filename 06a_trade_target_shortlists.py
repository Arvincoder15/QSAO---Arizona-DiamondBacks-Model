import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------
# Paths
# -----------------------
SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "data" / "raw"
OUT_DIR = SCRIPT_DIR / "outputs" / "trade_targets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BR_XLSX = RAW_DIR / "BR Baseball Data 2021-2025.xlsx"
SAV_BAT = RAW_DIR / "Savant Batter 2021-2025.csv"
SAV_PIT = RAW_DIR / "Savant Pitcher 2021-2025.csv"

# -----------------------
# Load 2025 sheets from BR
# -----------------------
br_bat = pd.read_excel(BR_XLSX, sheet_name="BATTER2025")
br_pit = pd.read_excel(BR_XLSX, sheet_name="PITCHER2025")

# Load Savant (all years) then filter 2025
sav_bat = pd.read_csv(SAV_BAT)
sav_pit = pd.read_csv(SAV_PIT)

sav_bat_25 = sav_bat[sav_bat["year"] == 2025].copy()
sav_pit_25 = sav_pit[sav_pit["year"] == 2025].copy()

# -----------------------
# Name cleaning helpers
# -----------------------
def clean_br_name(name):
    if pd.isna(name): return name
    return str(name).replace("*", "").replace("#", "").strip().lower()

def savant_to_br_name(name):
    if pd.isna(name): return name
    last, first = str(name).split(",")
    return f"{first.strip()} {last.strip()}".lower()

br_bat["player_clean"] = br_bat["Player"].map(clean_br_name)
br_pit["player_clean"] = br_pit["Player"].map(clean_br_name)

sav_bat_25["player_clean"] = sav_bat_25["last_name, first_name"].map(savant_to_br_name)
sav_pit_25["player_clean"] = sav_pit_25["last_name, first_name"].map(savant_to_br_name)

# -----------------------
# Merge BR <-> Savant (2025)
# -----------------------
bat = br_bat.merge(
    sav_bat_25[["player_clean", "xwoba", "xslg", "k_percent", "bb_percent", "barrel_batted_rate"]],
    on="player_clean",
    how="left"
)

pit = br_pit.merge(
    sav_pit_25[["player_clean", "p_era", "xwoba", "whiff_percent", "k_percent", "bb_percent", "hard_hit_percent"]],
    on="player_clean",
    how="left"
)

# -----------------------
# Exclude ARI (targets must be outside org)
# -----------------------
bat = bat[bat["Team"] != "ARI"].copy()
pit = pit[pit["Team"] != "ARI"].copy()

# -----------------------
# Bullpen targets: relievers only
# Rule: GS < 10 and IP >= 30 (you can loosen to 20 if you want more names)
# -----------------------
rel = pit[(pit["GS"] < 10) & (pit["IP"] >= 30)].copy()

# Score relievers (higher = better fit)
# Encourage: whiff, K%; discourage: BB%, xwOBA allowed, hard-hit%
score_cols = ["whiff_percent", "k_percent", "bb_percent", "xwoba", "hard_hit_percent", "p_era"]
for c in score_cols:
    if c in rel.columns:
        rel[c] = pd.to_numeric(rel[c], errors="coerce")

# Fill missing with medians so we don't drop good candidates
for c in score_cols:
    if c in rel.columns:
        rel[c] = rel[c].fillna(rel[c].median())

def z(s):
    return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

rel["relief_fit_score"] = (
    0.35 * z(rel["whiff_percent"]) +
    0.30 * z(rel["k_percent"]) -
    0.20 * z(rel["bb_percent"]) -
    0.20 * z(rel["xwoba"]) -
    0.10 * z(rel["hard_hit_percent"]) -
    0.10 * z(rel["p_era"])
)

rel_targets = rel.sort_values("relief_fit_score", ascending=False).head(25)
rel_targets.to_csv(OUT_DIR / "mlb2025_reliever_targets_top25.csv", index=False)

# -----------------------
# Impact bat targets
# Rule: PA >= 300 (regulars/platoons with real usage)
# Score bats: encourage xwOBA, xSLG, barrels, BB%; discourage K%
# -----------------------
bat = bat.copy()
for c in ["xwoba", "xslg", "barrel_batted_rate", "bb_percent", "k_percent"]:
    if c in bat.columns:
        bat[c] = pd.to_numeric(bat[c], errors="coerce")
        bat[c] = bat[c].fillna(bat[c].median())

bat_pool = bat[bat["PA"] >= 300].copy()

bat_pool["bat_fit_score"] = (
    0.40 * z(bat_pool["xwoba"]) +
    0.30 * z(bat_pool["xslg"]) +
    0.15 * z(bat_pool["barrel_batted_rate"]) +
    0.10 * z(bat_pool["bb_percent"]) -
    0.15 * z(bat_pool["k_percent"])
)

bat_targets = bat_pool.sort_values("bat_fit_score", ascending=False).head(25)
bat_targets.to_csv(OUT_DIR / "mlb2025_batter_targets_top25.csv", index=False)

print("✅ Step 6A complete — target lists saved to outputs/trade_targets/")
print("Reliever targets:", OUT_DIR / "mlb2025_reliever_targets_top25.csv")
print("Batter targets:", OUT_DIR / "mlb2025_batter_targets_top25.csv")
