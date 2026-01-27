import os
import osmnx as ox
import pandas as pd


CENTER_LAT = 13.04      # degrees north
CENTER_LON = 80.23      # degrees east
DIST_M = 1000           # 1000 m in each direction → ~2 km x 2 km box

CACHE_DIR = "cache"
GRAPHML_PATH = os.path.join(CACHE_DIR, "tnagar_2km.graphml")
EDGES_CSV_PATH = os.path.join(CACHE_DIR, "tnagar_edges.csv")


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 1) Download driveable road network for a 2 km x 2 km box
    print("Downloading T. Nagar graph...")
    G = ox.graph_from_point(
        (CENTER_LAT, CENTER_LON),
        dist=DIST_M,
        network_type="drive"
    )

    # 2) Save the graph for later use (Dijkstra, animation, etc.)
    ox.save_graphml(G, GRAPHML_PATH)
    print(f"Saved graphml: {GRAPHML_PATH}")

    # 3) Convert to GeoDataFrames and export a simple edges CSV
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

    # Give each edge a simple id column for joining with hazard later
    gdf_edges = gdf_edges.reset_index().reset_index().rename(
        columns={"index": "edge_id"}
    )

    # Keep key columns; you can add more if you like
    cols = [
        "edge_id",
        "u", "v",                # from_node, to_node
        "length",                # metres
        "highway",
        "name",
        "geometry"
    ]
    for c in cols:
        if c not in gdf_edges.columns:
            gdf_edges[c] = None

    gdf_edges[cols].to_csv(EDGES_CSV_PATH, index=False)
    print(f"Saved edges CSV: {EDGES_CSV_PATH}")


if __name__ == "__main__":
    main()
