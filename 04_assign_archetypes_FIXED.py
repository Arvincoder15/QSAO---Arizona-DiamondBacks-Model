import pandas as pd
from pathlib import Path
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_DIR = SCRIPT_DIR / "outputs" / "models"
OUT_DIR = SCRIPT_DIR / "outputs" / "archetypes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAT = MODEL_DIR / "ari_batters_2025_WAR_projection.csv"
PIT = MODEL_DIR / "ari_pitchers_2025_WAR_projection.csv"

bat = pd.read_csv(BAT)
pit = pd.read_csv(PIT)

def impute_median(df, cols):
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].fillna(df[c].median())
    return df

# -----------------------
# HITTING ARCHETYPES (team-relative percentiles)
# -----------------------
bat_key = ["xwoba", "xslg", "k_percent", "bb_percent", "barrel_batted_rate"]
bat_imp = impute_median(bat, bat_key)

q = {}
for c in bat_key:
    if c in bat_imp.columns:
        q[c] = {
            "p30": bat_imp[c].quantile(0.30),
            "p50": bat_imp[c].quantile(0.50),
            "p70": bat_imp[c].quantile(0.70),
        }

def hit_arch(r):
    # if core stuff missing entirely, call unknown
    if "xwoba" not in bat_imp.columns or pd.isna(r.get("xwoba", np.nan)):
        return "Unknown / Low Sample"

    xw = r["xwoba"]; xs = r.get("xslg", np.nan)
    k  = r.get("k_percent", np.nan); bb = r.get("bb_percent", np.nan)
    br = r.get("barrel_batted_rate", np.nan)

    # Power Bat: top 30% power + top 30% barrels on team
    if ("xslg" in q and "barrel_batted_rate" in q and
        xs >= q["xslg"]["p70"] and br >= q["barrel_batted_rate"]["p70"]):
        return "Power Bat"

    # Power–Contact Hybrid: top 30% xwoba AND above-median xslg AND below-median K%
    if ("xwoba" in q and "xslg" in q and "k_percent" in q and
        xw >= q["xwoba"]["p70"] and xs >= q["xslg"]["p50"] and k <= q["k_percent"]["p50"]):
        return "Power–Contact Hybrid"

    # High-OBP / Table Setter: top 30% BB% and not high K%
    if ("bb_percent" in q and "k_percent" in q and
        bb >= q["bb_percent"]["p70"] and k <= q["k_percent"]["p70"]):
        return "High-OBP / Table Setter"

    # Contact-First: bottom 30% K% and below-median power
    if ("k_percent" in q and "xslg" in q and
        k <= q["k_percent"]["p30"] and xs <= q["xslg"]["p50"]):
        return "Contact-First Bat"

    return "Replacement-Level / Depth"

bat["hitting_archetype"] = bat_imp.apply(hit_arch, axis=1)

# -----------------------
# PITCHING ARCHETYPES (team-relative percentiles)
# -----------------------
pit_key = ["p_era", "xwoba", "whiff_percent", "k_percent", "bb_percent", "hard_hit_percent"]
pit_imp = impute_median(pit, pit_key)

pq = {}
for c in pit_key:
    if c in pit_imp.columns:
        pq[c] = {
            "p25": pit_imp[c].quantile(0.25),
            "p40": pit_imp[c].quantile(0.40),
            "p60": pit_imp[c].quantile(0.60),
            "p75": pit_imp[c].quantile(0.75),
        }

def pit_arch(r):
    if "p_era" not in pit_imp.columns or pd.isna(r.get("p_era", np.nan)):
        return "Unknown / Low Sample"

    is_starter = ("GS" in r and r["GS"] >= 10)

    era = r.get("p_era", np.nan)
    wh  = r.get("whiff_percent", np.nan)
    k   = r.get("k_percent", np.nan)
    bb  = r.get("bb_percent", np.nan)
    hh  = r.get("hard_hit_percent", np.nan)

    if is_starter:
        # Frontline: top whiff + strong run prevention
        if (("whiff_percent" in pq and "p_era" in pq) and
            wh >= pq["whiff_percent"]["p75"] and era <= pq["p_era"]["p40"]):
            return "Frontline Starter"
        if ("p_era" in pq and era <= pq["p_era"]["p60"]):
            return "Mid-Rotation Starter"
        return "Back-End / Contact Starter"

    # Relievers
    if (("whiff_percent" in pq and "k_percent" in pq) and
        wh >= pq["whiff_percent"]["p75"] and k >= pq["k_percent"]["p75"]):
        return "High-Leverage Power Reliever"

    if (("bb_percent" in pq and "hard_hit_percent" in pq) and
        bb <= pq["bb_percent"]["p25"] and hh <= pq["hard_hit_percent"]["p60"]):
        return "Command / Contact Reliever"

    return "Low-Leverage / Depth Arm"

pit["pitching_archetype"] = pit_imp.apply(pit_arch, axis=1)

# Save
bat.to_csv(OUT_DIR / "ari_batters_2025_with_archetypes.csv", index=False)
pit.to_csv(OUT_DIR / "ari_pitchers_2025_with_archetypes.csv", index=False)

print("✅ Archetypes assigned (percentile-based)")
print("Batters:", bat["hitting_archetype"].value_counts().to_dict())
print("Pitchers:", pit["pitching_archetype"].value_counts().to_dict())
print("Saved to:", OUT_DIR)
