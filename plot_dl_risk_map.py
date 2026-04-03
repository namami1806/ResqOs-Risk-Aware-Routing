import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# -----------------------------
# Load road network
# -----------------------------
edges = gpd.read_file("anna_nagar_edges.geojson")

# Fix osmid column (sometimes stored as list/string)
edges["osmid"] = edges["osmid"].astype(str).str.extract(r"(\d+)")[0]
edges["osmid"] = pd.to_numeric(edges["osmid"], errors="coerce")

edges = edges.dropna(subset=["osmid"])
edges["osmid"] = edges["osmid"].astype(int)

# -----------------------------
# Load DL risk results
# -----------------------------
risk_data = pd.read_csv("edges_with_dl_risk.csv")

risk_data["edge_id"] = pd.to_numeric(risk_data["edge_id"], errors="coerce")
risk_data = risk_data.dropna(subset=["edge_id"])
risk_data["edge_id"] = risk_data["edge_id"].astype(int)

# -----------------------------
# Merge datasets
# -----------------------------
edges = edges.merge(
    risk_data,
    left_on="osmid",
    right_on="edge_id"
)

# -----------------------------
# Plot hazard intensity map
# -----------------------------
fig, ax = plt.subplots(figsize=(10,10))

edges.plot(
    column="dl_risk_score",
    cmap="Reds",
    linewidth=2,
    legend=True,
    ax=ax
)

# Clean map appearance
ax.set_axis_off()

plt.title(
    "Deep Learning Hazard Intensity Map",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()
plt.show()

