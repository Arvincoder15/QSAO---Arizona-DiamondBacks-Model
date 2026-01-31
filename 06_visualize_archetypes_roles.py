import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------
# Paths
# -----------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ARCH_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR = SCRIPT_DIR / "outputs" / "visuals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT_FILE = ARCH_DIR / "ari_batters_2025_with_archetypes_and_roles.csv"
PIT_FILE = ARCH_DIR / "ari_pitchers_2025_with_archetypes_and_roles.csv"

# -----------------------
# Load
# -----------------------
bat = pd.read_csv(BAT_FILE)
pit = pd.read_csv(PIT_FILE)

# -----------------------
# Helpers
# -----------------------
def save_bar(series, title, xlabel, ylabel, filename):
    plt.figure()
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=200)
    plt.close()

def save_pie(series, title, filename):
    plt.figure()
    series.plot(kind="pie", autopct="%1.0f%%")
    plt.title(title)
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=200)
    plt.close()

# -----------------------
# 1) Hitting Archetypes (bar)
# -----------------------
bat_arch = bat["hitting_archetype"].value_counts()
save_bar(
    bat_arch,
    "Arizona Diamondbacks — Hitting Archetype Distribution (2025)",
    "Hitting Archetype",
    "Number of Players",
    "ari_hitting_archetypes_bar.png"
)

# -----------------------
# 2) Pitching Archetypes (bar)
# -----------------------
pit_arch = pit["pitching_archetype"].value_counts()
save_bar(
    pit_arch,
    "Arizona Diamondbacks — Pitching Archetype Distribution (2025)",
    "Pitching Archetype",
    "Number of Pitchers",
    "ari_pitching_archetypes_bar.png"
)

# -----------------------
# 3) Pitching Roles (pie)
# -----------------------
pit_roles = pit["pitching_role"].value_counts()
save_pie(
    pit_roles,
    "Pitching Role Split (Starter vs Bullpen)",
    "ari_pitching_roles_pie.png"
)

# -----------------------
# 4) Hitting Roles (pie)
# -----------------------
bat_roles = bat["hitting_role"].value_counts()
save_pie(
    bat_roles,
    "Hitting Role Distribution",
    "ari_hitting_roles_pie.png"
)

print("✅ Visuals saved to:", OUT_DIR)
for f in [
    "ari_hitting_archetypes_bar.png",
    "ari_pitching_archetypes_bar.png",
    "ari_pitching_roles_pie.png",
    "ari_hitting_roles_pie.png",
]:
    print(" -", f)
