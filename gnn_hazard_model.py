import pandas as pd
import geopandas as gpd
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from sklearn.preprocessing import MinMaxScaler

# -----------------------------
# Load hazard dataset
# -----------------------------
hazard = pd.read_csv("hazard_data_demo.csv")

# -----------------------------
# Load road network
# -----------------------------
edges = gpd.read_file("anna_nagar_edges.geojson")

# clean osmid
edges["osmid"] = edges["osmid"].astype(str).str.extract(r"(\d+)")[0]
edges["osmid"] = pd.to_numeric(edges["osmid"], errors="coerce")

edges = edges.dropna(subset=["osmid"])
edges["osmid"] = edges["osmid"].astype(int)

# -----------------------------
# Merge hazard data
# -----------------------------
hazard["edge_id"] = pd.to_numeric(hazard["edge_id"], errors="coerce")
hazard = hazard.dropna(subset=["edge_id"])
hazard["edge_id"] = hazard["edge_id"].astype(int)

edges = edges.merge(hazard, left_on="osmid", right_on="edge_id")

# -----------------------------
# Create node index mapping
# -----------------------------
nodes = pd.concat([edges["u"], edges["v"]]).unique()

node_to_index = {node: i for i, node in enumerate(nodes)}

edges["u_idx"] = edges["u"].map(node_to_index)
edges["v_idx"] = edges["v"].map(node_to_index)

# -----------------------------
# Node features
# -----------------------------
features = edges[["water_level", "crowd_density"]].values

scaler = MinMaxScaler()
X = scaler.fit_transform(features)

x = torch.tensor(X, dtype=torch.float)

# -----------------------------
# Graph connectivity
# -----------------------------
edge_index = torch.tensor(
    [edges["u_idx"].values, edges["v_idx"].values],
    dtype=torch.long
)

# -----------------------------
# Labels
# -----------------------------
y = torch.tensor(
    (edges["risk_score"] > 0.5).astype(int).values,
    dtype=torch.long
)

data = Data(x=x, edge_index=edge_index, y=y)

# -----------------------------
# Graph Neural Network
# -----------------------------
class GNN(torch.nn.Module):

    def __init__(self):
        super().__init__()

        self.conv1 = GCNConv(2, 8)
        self.conv2 = GCNConv(8, 2)

    def forward(self, data):

        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)

        x = self.conv2(x, edge_index)

        return x

model = GNN()

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# -----------------------------
# Training
# -----------------------------
for epoch in range(100):

    optimizer.zero_grad()

    out = model(data)

    loss = F.cross_entropy(out, data.y)

    loss.backward()

    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch} Loss {loss.item():.4f}")

# -----------------------------
# Predictions
# -----------------------------
pred = model(data).argmax(dim=1)

edges["gnn_risk"] = pred.numpy()

# -----------------------------
# Save results
# -----------------------------
edges.to_file("gnn_risk_edges.geojson")

print("GNN hazard predictions saved.")