import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ARCH_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT_FILE = ARCH_DIR / "ari_batters_2025_with_archetypes.csv"

bat = pd.read_csv(BAT_FILE)

if "PA" not in bat.columns:
    raise ValueError("PA column not found in batter file. Cannot assign hitter roles.")

def hitter_role(pa):
    if pd.isna(pa):
        return "Unknown"
    pa = float(pa)
    if pa >= 450:
        return "Everyday Player"
    if pa >= 250:
        return "Platoon / Regular"
    if pa >= 100:
        return "Bench / Utility"
    return "Depth / Limited Sample"

bat["hitting_role"] = bat["PA"].apply(hitter_role)

bat.to_csv(OUT_DIR / "ari_batters_2025_with_archetypes_and_roles.csv", index=False)

print("✅ Hitting roles added")
print(bat["hitting_role"].value_counts().to_dict())
print(f"Saved to: {OUT_DIR}")
