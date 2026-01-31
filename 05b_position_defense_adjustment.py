import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARCH_DIR = BASE / "outputs" / "archetypes"
DEC_DIR  = BASE / "outputs" / "decisions"
OUT_DIR  = DEC_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT_FILE = ARCH_DIR / "ari_batters_2025_with_archetypes_and_roles.csv"

bat = pd.read_csv(BAT_FILE)

# -----------------------
# 1) Find a position column
# -----------------------
pos_col = None
for c in ["Pos", "Position", "pos", "position"]:
    if c in bat.columns:
        pos_col = c
        break

if pos_col is None:
    print("⚠️ No position column found (Pos/Position).")
    print("We can still explain that BR WAR includes positional+defense, but cannot add multipliers.")
    # Save unchanged with a note
    bat.to_csv(OUT_DIR / "ari_batters_2025_adjusted.csv", index=False)
    raise SystemExit

# Convert position strings into a primary position
def primary_pos(p):
    if pd.isna(p): return "UNK"
    # Some BR formats: "1B", "2B", "SS", "CF", "LF", "RF", "C", "DH", "3B"
    # Sometimes multiple: "2B/SS" or "LF-RF"
    s = str(p).replace("-", "/").upper()
    return s.split("/")[0].strip()

bat["primary_pos"] = bat[pos_col].apply(primary_pos)

# -----------------------
# 2) Positional scarcity multipliers
# -----------------------
pos_mult = {
    "C": 1.10, "SS": 1.10, "CF": 1.10,
    "2B": 1.05, "3B": 1.05,
    "RF": 1.00, "LF": 1.00,
    "OF": 1.00,  # sometimes used
    "1B": 0.95, "DH": 0.95,
    "UNK": 1.00
}

bat["pos_multiplier"] = bat["primary_pos"].map(pos_mult).fillna(1.00)

# -----------------------
# 3) Defensive proxy (optional)
# -----------------------
# We'll look for common BR-style defense columns.
def_col = None
for c in ["dWAR", "Rfield", "Def", "Fld", "fielding_runs"]:
    if c in bat.columns:
        def_col = c
        break

# Defense bonus: small weight so it nudges, doesn't dominate
# If defense column exists, scale it lightly.
bat["defense_bonus"] = 0.0
if def_col is not None:
    # Fill missing defense with 0 so it doesn't break
    bat[def_col] = pd.to_numeric(bat[def_col], errors="coerce").fillna(0.0)
    bat["defense_bonus"] = 0.15 * bat[def_col]   # light weight

# -----------------------
# 4) Compute adjusted projected WAR
# -----------------------
if "proj_WAR_600" not in bat.columns:
    raise ValueError("proj_WAR_600 not found. Make sure you're using the 2025 projection file with roles/archetypes.")

bat["adj_proj_WAR_600"] = bat["proj_WAR_600"] * bat["pos_multiplier"] + bat["defense_bonus"]

# -----------------------
# Save
# -----------------------
bat.sort_values("adj_proj_WAR_600", ascending=False).to_csv(
    OUT_DIR / "ari_batters_2025_adjusted.csv", index=False
)

print("✅ Positional + defense adjustment applied")
print("Position column used:", pos_col)
print("Defense column used:", def_col if def_col else "None")
print("Saved to outputs/decisions/ari_batters_2025_adjusted.csv")
