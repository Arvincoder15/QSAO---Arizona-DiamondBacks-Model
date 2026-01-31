import pandas as pd
from pathlib import Path

# -----------------------
# Paths
# -----------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ARCH_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PIT_FILE = ARCH_DIR / "ari_pitchers_2025_with_archetypes.csv"

# -----------------------
# Load
# -----------------------
pit = pd.read_csv(PIT_FILE)

# -----------------------
# Role tagging
# -----------------------
def pitching_role(row):
    if "GS" not in pit.columns:
        return "Unknown"
    if row["GS"] >= 10:
        return "Starter"
    return "Bullpen"

pit["pitching_role"] = pit.apply(pitching_role, axis=1)

# -----------------------
# Save
# -----------------------
pit.to_csv(OUT_DIR / "ari_pitchers_2025_with_archetypes_and_roles.csv", index=False)

print("✅ Pitching roles added")
print(pit["pitching_role"].value_counts().to_dict())
print(f"Saved to: {OUT_DIR}")
