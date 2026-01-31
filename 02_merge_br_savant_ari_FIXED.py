import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data" / "processed"
OUT_DIR = SCRIPT_DIR / "outputs" / "features"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BR_BAT = DATA_DIR / "ARI_BR_batters_2021_2025.csv"
BR_PIT = DATA_DIR / "ARI_BR_pitchers_2021_2025.csv"
SAV_BAT = DATA_DIR / "ARI_Savant_batters_2021_2025.csv"
SAV_PIT = DATA_DIR / "ARI_Savant_pitchers_2021_2025.csv"

br_bat = pd.read_csv(BR_BAT)
br_pit = pd.read_csv(BR_PIT)
sav_bat = pd.read_csv(SAV_BAT)
sav_pit = pd.read_csv(SAV_PIT)

def clean_br_name(name):
    if pd.isna(name): return name
    return str(name).replace("*", "").replace("#", "").strip().lower()

def savant_to_br_name(name):
    if pd.isna(name): return name
    last, first = str(name).split(",")
    return f"{first.strip()} {last.strip()}".lower()

br_bat["player_clean"] = br_bat["Player"].map(clean_br_name)
br_pit["player_clean"] = br_pit["Player"].map(clean_br_name)

sav_bat["player_clean"] = sav_bat["last_name, first_name"].map(savant_to_br_name)
sav_pit["player_clean"] = sav_pit["last_name, first_name"].map(savant_to_br_name)

sav_bat = sav_bat.rename(columns={"year": "Year"})
sav_pit = sav_pit.rename(columns={"year": "Year"})

# ✅ Use correct Savant column names (lowercase)
bat_savant_features = [
    "xwoba", "xslg", "xba",
    "barrel_batted_rate", "hard_hit_percent",
    "exit_velocity_avg", "sweet_spot_percent",
    "k_percent", "bb_percent",
]

pit_savant_features = [
    "p_era",          # proxy for run prevention (Savant expected-style field in your file)
    "xwoba",
    "whiff_percent",
    "k_percent", "bb_percent",
    "hard_hit_percent", "barrel_batted_rate",
    "exit_velocity_avg",
]

sav_bat_small = sav_bat[["player_clean", "Year"] + [c for c in bat_savant_features if c in sav_bat.columns]].copy()
sav_pit_small = sav_pit[["player_clean", "Year"] + [c for c in pit_savant_features if c in sav_pit.columns]].copy()

batters_full = br_bat.merge(sav_bat_small, on=["player_clean", "Year"], how="left")
pitchers_full = br_pit.merge(sav_pit_small, on=["player_clean", "Year"], how="left")

batters_full.to_csv(OUT_DIR / "ari_batters_features_2021_2025.csv", index=False)
pitchers_full.to_csv(OUT_DIR / "ari_pitchers_features_2021_2025.csv", index=False)

print("✅ Fixed feature tables saved to outputs/features/")
print("Batters cols added:", [c for c in bat_savant_features if c in batters_full.columns])
print("Pitchers cols added:", [c for c in pit_savant_features if c in pitchers_full.columns])
