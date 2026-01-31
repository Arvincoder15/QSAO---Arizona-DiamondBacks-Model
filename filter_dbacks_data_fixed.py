import pandas as pd
from pathlib import Path

TEAM_ABBR = "ARI"
YEARS = [2021, 2022, 2023, 2024, 2025]

SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "data" / "raw"
OUT_DIR = SCRIPT_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BR_XLSX = RAW_DIR / "BR Baseball Data 2021-2025.xlsx"
SAVANT_BATTER = RAW_DIR / "Savant Batter 2021-2025.csv"
SAVANT_PITCHER = RAW_DIR / "Savant Pitcher 2021-2025.csv"

# -----------------------
# Load BR data (BATTERYYYY / PITCHERYYYY sheets)
# -----------------------
print("Loading Baseball Reference (BR) data...")

xls = pd.ExcelFile(BR_XLSX)

def load_br_sheets(prefix: str) -> pd.DataFrame:
    frames = []
    for yr in YEARS:
        sheet = f"{prefix}{yr}"  # e.g., BATTER2025
        if sheet not in xls.sheet_names:
            raise ValueError(f"Missing sheet: {sheet}. Found: {xls.sheet_names}")
        df = pd.read_excel(BR_XLSX, sheet_name=sheet)
        df["Year"] = yr
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

br_batters = load_br_sheets("BATTER")
br_pitchers = load_br_sheets("PITCHER")

# Filter BR to Arizona
br_batters_ari = br_batters[(br_batters["Team"] == TEAM_ABBR)].copy()
br_pitchers_ari = br_pitchers[(br_pitchers["Team"] == TEAM_ABBR)].copy()

# -----------------------
# Load Savant data (no team column -> filter by BR ARI player list per year)
# -----------------------
print("Loading Baseball Savant data...")

savant_batters = pd.read_csv(SAVANT_BATTER)
savant_pitchers = pd.read_csv(SAVANT_PITCHER)

# Savant uses "last_name, first_name" and "year"
NAME_COL = "last_name, first_name"
YEAR_COL = "year"

required_batter_cols = {NAME_COL, YEAR_COL}
required_pitcher_cols = {NAME_COL, YEAR_COL}

if not required_batter_cols.issubset(set(savant_batters.columns)):
    raise ValueError(f"Savant batter file missing columns: {required_batter_cols - set(savant_batters.columns)}")
if not required_pitcher_cols.issubset(set(savant_pitchers.columns)):
    raise ValueError(f"Savant pitcher file missing columns: {required_pitcher_cols - set(savant_pitchers.columns)}")

# Build ARI player-name sets per year from BR
# BR "Player" is "First Last", Savant is "Last, First" — convert BR names to Savant format.
def to_savant_name(br_player: str) -> str:
    # Remove common annotations like * # in BR names
    clean = str(br_player).replace("*", "").replace("#", "").strip()
    parts = clean.split()
    if len(parts) < 2:
        return clean  # fallback
    first = " ".join(parts[:-1])
    last = parts[-1]
    return f"{last}, {first}"

ari_batter_names_by_year = {
    yr: set(br_batters_ari[br_batters_ari["Year"] == yr]["Player"].dropna().map(to_savant_name))
    for yr in YEARS
}
ari_pitcher_names_by_year = {
    yr: set(br_pitchers_ari[br_pitchers_ari["Year"] == yr]["Player"].dropna().map(to_savant_name))
    for yr in YEARS
}

# Filter Savant by (year AND name in that year's ARI list)
savant_batters_ari_frames = []
for yr in YEARS:
    names = ari_batter_names_by_year[yr]
    savant_batters_ari_frames.append(
        savant_batters[(savant_batters[YEAR_COL] == yr) & (savant_batters[NAME_COL].isin(names))].copy()
    )
savant_batters_ari = pd.concat(savant_batters_ari_frames, ignore_index=True)

savant_pitchers_ari_frames = []
for yr in YEARS:
    names = ari_pitcher_names_by_year[yr]
    savant_pitchers_ari_frames.append(
        savant_pitchers[(savant_pitchers[YEAR_COL] == yr) & (savant_pitchers[NAME_COL].isin(names))].copy()
    )
savant_pitchers_ari = pd.concat(savant_pitchers_ari_frames, ignore_index=True)

# -----------------------
# Save outputs
# -----------------------
print("Saving filtered datasets...")

br_batters_ari.to_csv(OUT_DIR / "ARI_BR_batters_2021_2025.csv", index=False)
br_pitchers_ari.to_csv(OUT_DIR / "ARI_BR_pitchers_2021_2025.csv", index=False)
savant_batters_ari.to_csv(OUT_DIR / "ARI_Savant_batters_2021_2025.csv", index=False)
savant_pitchers_ari.to_csv(OUT_DIR / "ARI_Savant_pitchers_2021_2025.csv", index=False)

print("✅ Done.")
print(f"BR batters ARI rows:   {len(br_batters_ari)}")
print(f"BR pitchers ARI rows:  {len(br_pitchers_ari)}")
print(f"Savant batters ARI rows:  {len(savant_batters_ari)}")
print(f"Savant pitchers ARI rows: {len(savant_pitchers_ari)}")
print(f"Outputs saved to: {OUT_DIR}")
