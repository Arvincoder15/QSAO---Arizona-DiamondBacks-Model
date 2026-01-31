import pandas as pd
from pathlib import Path

# -----------------------
# Paths
# -----------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ARCH_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR = SCRIPT_DIR / "outputs" / "decisions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT_FILE = ARCH_DIR / "ari_batters_2025_with_archetypes_and_roles.csv"
PIT_FILE = ARCH_DIR / "ari_pitchers_2025_with_archetypes_and_roles.csv"

# -----------------------
# Load
# -----------------------
bat = pd.read_csv(BAT_FILE)
pit = pd.read_csv(PIT_FILE)

# -----------------------
# Helper
# -----------------------
def median(series):
    return series.median()

# -----------------------
# BATTERS: Core vs Surplus
# -----------------------
bat_war_med = median(bat["proj_WAR_600"])

bat["core_flag"] = (
    (bat["proj_WAR_600"] >= bat_war_med) &
    (bat["hitting_role"] == "Everyday Player") &
    (bat["Age"] <= 32)
)

bat["surplus_flag"] = (
    (bat["proj_WAR_600"] < bat_war_med) |
    (bat["hitting_role"].isin(["Bench / Utility"])) &
    (bat["Age"] >= 27)
)

bat_core = bat[bat["core_flag"]].sort_values("proj_WAR_600", ascending=False)
bat_surplus = bat[bat["surplus_flag"]].sort_values("proj_WAR_600")

# -----------------------
# PITCHERS: Core vs Surplus
# -----------------------
pit_war_med = median(pit["proj_WAR_180"])

pit["core_flag"] = (
    (pit["proj_WAR_180"] >= pit_war_med) &
    (pit["pitching_role"] == "Starter") &
    (pit["Age"] <= 32)
)

pit["surplus_flag"] = (
    (pit["proj_WAR_180"] < pit_war_med) |
    (pit["pitching_role"] == "Bullpen") &
    (pit["Age"] >= 27)
)

pit_core = pit[pit["core_flag"]].sort_values("proj_WAR_180", ascending=False)
pit_surplus = pit[pit["surplus_flag"]].sort_values("proj_WAR_180")

# -----------------------
# TEAM NEEDS SUMMARY
# -----------------------
bat_needs = bat.groupby(["hitting_archetype", "hitting_role"]).size().reset_index(name="count")
pit_needs = pit.groupby(["pitching_archetype", "pitching_role"]).size().reset_index(name="count")

# -----------------------
# Save outputs
# -----------------------
bat_core.to_csv(OUT_DIR / "ari_core_batters.csv", index=False)
bat_surplus.to_csv(OUT_DIR / "ari_surplus_batters.csv", index=False)

pit_core.to_csv(OUT_DIR / "ari_core_pitchers.csv", index=False)
pit_surplus.to_csv(OUT_DIR / "ari_surplus_pitchers.csv", index=False)

bat_needs.to_csv(OUT_DIR / "ari_batter_archetype_summary.csv", index=False)
pit_needs.to_csv(OUT_DIR / "ari_pitching_archetype_summary.csv", index=False)

print("✅ Step 5 complete")
print(f"Core batters: {len(bat_core)} | Surplus batters: {len(bat_surplus)}")
print(f"Core pitchers: {len(pit_core)} | Surplus pitchers: {len(pit_surplus)}")
print("Outputs saved to outputs/decisions/")
