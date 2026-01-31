import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

SCRIPT_DIR = Path(__file__).resolve().parent
FEAT_DIR = SCRIPT_DIR / "outputs" / "features"
OUT_DIR = SCRIPT_DIR / "outputs" / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT = FEAT_DIR / "ari_batters_features_2021_2025.csv"
PIT = FEAT_DIR / "ari_pitchers_features_2021_2025.csv"

bat = pd.read_csv(BAT)
pit = pd.read_csv(PIT)

# Rate targets
bat = bat[bat["PA"] >= 150].copy()
bat["WAR_per_600"] = bat["WAR"] / bat["PA"] * 600

pit = pit[pit["IP"] >= 40].copy()
pit["WAR_per_180"] = pit["WAR"] / pit["IP"] * 180

bat_features = [c for c in [
    "Age", "xwoba", "xslg", "xba",
    "barrel_batted_rate", "hard_hit_percent",
    "exit_velocity_avg", "sweet_spot_percent",
    "k_percent", "bb_percent"
] if c in bat.columns]

pit_features = [c for c in [
    "Age", "p_era", "xwoba",
    "whiff_percent", "k_percent", "bb_percent",
    "hard_hit_percent", "barrel_batted_rate",
    "exit_velocity_avg"
] if c in pit.columns]

train_bat = bat[bat["Year"] <= 2024].copy()
test_bat  = bat[bat["Year"] == 2025].copy()

train_pit = pit[pit["Year"] <= 2024].copy()
test_pit  = pit[pit["Year"] == 2025].copy()

# -----------------------
# ✅ Recency weighting (edit these if you want)
# -----------------------
YEAR_WEIGHTS = {2021: 0.4, 2022: 0.6, 2023: 0.8, 2024: 1.0}

train_bat["sample_w"] = train_bat["Year"].map(YEAR_WEIGHTS).fillna(0.5)
train_pit["sample_w"] = train_pit["Year"].map(YEAR_WEIGHTS).fillna(0.5)

bat_model = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

pit_model = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

# -----------------------
# ✅ Fit with sample weights (Pipeline passes these to Ridge)
# -----------------------
bat_model.fit(
    train_bat[bat_features],
    train_bat["WAR_per_600"],
    ridge__sample_weight=train_bat["sample_w"]
)

pit_model.fit(
    train_pit[pit_features],
    train_pit["WAR_per_180"],
    ridge__sample_weight=train_pit["sample_w"]
)

test_bat["proj_WAR_600"] = bat_model.predict(test_bat[bat_features])
test_pit["proj_WAR_180"] = pit_model.predict(test_pit[pit_features])

bat_rank = test_bat.sort_values("proj_WAR_600", ascending=False)
pit_rank = test_pit.sort_values("proj_WAR_180", ascending=False)

bat_rank.to_csv(OUT_DIR / "ari_batters_2025_WAR_projection.csv", index=False)
pit_rank.to_csv(OUT_DIR / "ari_pitchers_2025_WAR_projection.csv", index=False)

print("✅ Weighted-year projections saved to outputs/models/")
print("Year weights used:", YEAR_WEIGHTS)
print("Batters features used:", bat_features)
print("Pitchers features used:", pit_features)
