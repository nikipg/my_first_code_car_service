# analyze.py
# Summary: avg_daily_km and load_factor are the strongest predictors of breakdown — not total
# odometer or age. Cars that drive more kilometres per day under heavier load fail at a much
# higher rate. Odometer and age alone are poor separators.
#
# This script loads fleet_history.csv, compares breakdown vs. non-breakdown groups column by
# column, builds a simple 0-100 risk score from the two separating factors, and prints all
# 120 cars ranked from highest to lowest risk.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --- 1. Compare group means: broke_down=1 vs broke_down=0 ---
broke = df[df["broke_down"] == 1]
fine  = df[df["broke_down"] == 0]

numeric_cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print("=== Group comparison (mean values) ===")
print(f"{'Column':<22} {'Broke down':>12} {'Did not':>12} {'Ratio':>8}")
print("-" * 56)
separators = []
for col in numeric_cols:
    b_mean = broke[col].mean()
    f_mean = fine[col].mean()
    ratio  = b_mean / f_mean if f_mean != 0 else float("inf")
    print(f"{col:<22} {b_mean:>12.2f} {f_mean:>12.2f} {ratio:>8.2f}")
    if ratio > 1.15 or ratio < 0.85:        # >15 % difference → meaningful separator
        separators.append(col)

print()
print("Separating factors (>15 % difference between groups):", separators)
print()

# --- 2. Build a simple 0–100 risk score from the separating factors ---
# Normalise each separator to [0, 1] then average them; multiply by 100.
if separators:
    score_parts = []
    for col in separators:
        col_min = df[col].min()
        col_max = df[col].max()
        span    = col_max - col_min
        if span > 0:
            score_parts.append((df[col] - col_min) / span)
    if score_parts:
        df["risk_score"] = sum(score_parts) / len(score_parts) * 100
    else:
        df["risk_score"] = 0.0
else:
    df["risk_score"] = 0.0

# --- 3. Print cars ranked by risk, highest first ---
ranked = df[["car_id", "risk_score", "broke_down"] + separators].sort_values(
    "risk_score", ascending=False
)

print("=== Cars ranked by breakdown risk (highest first) ===")
print(ranked.to_string(index=False, float_format="%.1f"))
