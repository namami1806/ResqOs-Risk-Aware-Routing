import os
import osmnx as ox
import pandas as pd

CACHE_DIR = "cache"
GRAPHML_PATH = os.path.join(CACHE_DIR, "tnagar_2km_with_risk.graphml")
OUTPUT_CSV = os.path.join(CACHE_DIR, "tnagar_edges_with_coordinates.csv")


def main():
    print("Loading graph with risk...")
    G = ox.load_graphml(GRAPHML_PATH)

    # Extract all edges with their attributes
    rows = []
    for u, v, key, data in G.edges(keys=True, data=True):
        row = {
            "u": u,
            "v": v,
            "key": key,
            "length": data.get("length", 0),
            "name": data.get("name", ""),
            "effective_cost": data.get("effective_cost", 0),
            "risk_score": data.get("risk_score", 0),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} edges to {OUTPUT_CSV}")
    print(df.head(10))

if __name__ == "__main__":
    main()

