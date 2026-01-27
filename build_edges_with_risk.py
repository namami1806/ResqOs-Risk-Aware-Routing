import pandas as pd
import numpy as np

# 1) Small helper: turn a number into 0..1 "low/medium/high" degrees
def tri_left(x, a, b):
    if x <= a:
        return 1.0
    if x >= b:
        return 0.0
    return (b - x) / (b - a)

def tri_right(x, a, b):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    return (x - a) / (b - a)

def tri_mid(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

# 2) Fuzzy-like membership for each input
def water_risk_level(water_cm):
    low = tri_left(water_cm, 0, 20)
    med = tri_mid(water_cm, 10, 30, 50)
    high = tri_right(water_cm, 40, 80)
    return low, med, high

def crowd_risk_level(crowd_ppm2):
    low = tri_left(crowd_ppm2, 0, 1.5)
    med = tri_mid(crowd_ppm2, 1.0, 2.5, 4.0)
    high = tri_right(crowd_ppm2, 3.0, 6.0)
    return low, med, high

def rain_risk_level(rain_intensity):
    low = tri_left(rain_intensity, 0, 20)
    med = tri_mid(rain_intensity, 10, 40, 70)
    high = tri_right(rain_intensity, 60, 100)
    return low, med, high

def light_risk_level(light_level):
    dark = tri_left(light_level, 0, 30)
    normal = tri_mid(light_level, 20, 50, 80)
    bright = tri_right(light_level, 60, 100)
    return dark, normal, bright

# 3) Combine them into ONE number: risk_score (0 to ~10)
def compute_risk_score(row):
    w_low, w_med, w_high = water_risk_level(row["water_level_cm"])
    c_low, c_med, c_high = crowd_risk_level(row["crowd_density_ppm2"])
    r_low, r_med, r_high = rain_risk_level(row["rain_intensity"])
    l_dark, l_norm, l_bright = light_risk_level(row["light_level"])

    # Rules:
    rule1 = max(w_high, c_high)        # very high risk
    rule2 = min(r_high, l_dark)        # high risk
    rule3 = min(w_med, c_med)          # medium risk
    rule4 = min(w_low, c_low, r_low, l_bright)  # low risk

    num = (rule4 * 2.0) + (rule3 * 5.0) + (rule2 * 8.0) + (rule1 * 10.0)
    den = (rule4 + rule3 + rule2 + rule1)
    if den == 0:
        return 0.0
    return num / den

# 4) Read edges + hazards, write tnagar_edges_with_risk.csv
def build_edges_with_risk():
    edges = pd.read_csv("cache/tnagar_edges.csv")
    hazard = pd.read_csv("cache/hazard_tnagar_real.csv")

    merged = edges.merge(hazard, left_on="edge_id", right_on="edge_id", how="left")

    # default safe values if no hazard row
    merged["water_level_cm"] = merged["water_level_cm"].fillna(0)
    merged["crowd_density_ppm2"] = merged["crowd_density_ppm2"].fillna(0.5)
    merged["rain_intensity"] = merged["rain_intensity"].fillna(0)
    merged["light_level"] = merged["light_level"].fillna(80)

    merged["risk_score"] = merged.apply(compute_risk_score, axis=1)

    if "length" in merged.columns:
        base = merged["length"].fillna(1.0)
    else:
        base = 1.0

    alpha = 5.0
    merged["effective_cost"] = base * (1.0 + alpha * merged["risk_score"] / 10.0)

    merged.to_csv("cache/tnagar_edges_with_risk.csv", index=False)
    print("Saved cache/tnagar_edges_with_risk.csv")

if __name__ == "__main__":
    build_edges_with_risk()
