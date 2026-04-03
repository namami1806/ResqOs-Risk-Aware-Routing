import geopandas as gpd
import matplotlib.pyplot as plt

# Load GNN prediction results
edges = gpd.read_file("gnn_risk_edges.geojson")

fig, ax = plt.subplots(figsize=(12,12))

# Base road network (light background)
edges.plot(
    ax=ax,
    color="#d0d0d0",
    linewidth=0.7,
    alpha=0.7
)

# Hazard roads overlay
hazards = edges[edges["gnn_risk"] == 1]

hazards.plot(
    ax=ax,
    color="#ff3b30",
    linewidth=3,
    label="Predicted Hazard"
)

# Styling
ax.set_axis_off()

plt.title(
    "Urban Hazard Detection (Graph Neural Network)",
    fontsize=16,
    fontweight="bold"
)

plt.legend()
plt.tight_layout()

plt.show()

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Ground truth (same rule used earlier)
edges["true_hazard"] = (
    (edges["water_level"] > 0.6) |
    (edges["crowd_density"] > 0.6)
)

y_true = edges["true_hazard"]

# GNN predictions
y_gnn = edges["gnn_risk"]

print("\nGraph Neural Network (GNN)")
print("Accuracy:", accuracy_score(y_true, y_gnn))
print("Precision:", precision_score(y_true, y_gnn))
print("Recall:", recall_score(y_true, y_gnn))
print("F1 Score:", f1_score(y_true, y_gnn))