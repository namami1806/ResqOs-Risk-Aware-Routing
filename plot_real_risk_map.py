import os
import osmnx as ox
import matplotlib.pyplot as plt

CACHE_DIR = "cache"
GRAPHML_PATH = os.path.join(CACHE_DIR, "tnagar_2km_with_risk.graphml")

def main():
    print("Loading graph with risk...")
    G = ox.load_graphml(GRAPHML_PATH)
    print("Nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges())

    print("Plotting...")
    fig, ax = ox.plot_graph(
        G,
        node_size=5,
        node_color="red",
        edge_color="black",
        edge_linewidth=0.8,
        bgcolor="white",
        show=True,
        close=False,
    )
    plt.show()

if __name__ == "__main__":
    main()
