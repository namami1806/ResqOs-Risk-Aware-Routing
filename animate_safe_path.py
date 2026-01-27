import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk

# force dark style
plt.style.use("dark_background")

# ------------------- JUNCTIONS (NAME -> NODE ID) -------------------
# IDs taken from tnagar_edges_with_risk (u/v columns).
# Edit the names if you want cleaner labels, but keep IDs as they are.
JUNCTIONS = {
    "Burkit Rd – Power House side": 247675521,
    "Venkatanarayana Rd near Burkit": 248697312,
    "South Usman × Burkit": 247074857,
    "Natesan St × South Usman": 247074856,
    "Burkit Rd – Dhandapani side": 247680992,
    "Venkatanarayana Rd junction": 248700472,
}
# -------------------------------------------------------------------


def build_graph_from_edges():
    edges = pd.read_csv("cache/tnagar_edges_with_risk.csv")
    G = nx.DiGraph()
    for _, row in edges.iterrows():
        u = row["u"]
        v = row["v"]
        cost = row["effective_cost"]
        G.add_edge(u, v, effective_cost=cost)
    return G


def run_animation(source, target):
    G = build_graph_from_edges()

    # shortest (safest) path using effective_cost
    path = nx.shortest_path(G, source=source, target=target,
                            weight="effective_cost")

    # layout (abstract but stable)
    pos = nx.spring_layout(G, k=0.1, iterations=80, seed=42)

    # ------------------- DARK THEME FIGURE -------------------
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("#111111")  # dark background

    # all edges in dim gray
    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        edge_color="#444444",
        width=0.5,
        alpha=0.6,
    )

    # path edges in bright neon green
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        edgelist=path_edges,
        edge_color="#00FF88",
        width=3.0,
    )

    # path nodes in bright blue
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        nodelist=path,
        node_color="#00BFFF",
        node_size=40,
    )

    # label only source & target
    id_to_name = {v: k for k, v in JUNCTIONS.items()}
    labels = {
        source: id_to_name.get(source, str(source)),
        target: id_to_name.get(target, str(target)),
    }
    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_color="white",
        font_size=8,
        ax=ax,
    )

    # ---------------------------------------------------------

    # coordinates of path nodes in order
    x_coords = [pos[n][0] for n in path]
    y_coords = [pos[n][1] for n in path]

    # moving point (traveller)
    point, = ax.plot(
        [x_coords[0]],
        [y_coords[0]],
        "o",
        color="#FFD700",
        markersize=10,
        zorder=5,
    )

    # trail line that grows with time
    trail, = ax.plot(
        [x_coords[0]],
        [y_coords[0]],
        color="#FFFF99",
        linewidth=2,
        alpha=0.9,
        zorder=4,
    )

    # ----------------- ZOOM-FRIENDLY SETTINGS -----------------
    # do NOT call ax.set_axis_off() so toolbar zoom/pan keeps working
    # instead, hide ticks and labels but keep axes/toolbar interactive
    ax.tick_params(left=False, bottom=False,
                   labelleft=False, labelbottom=False)

    # optional: auto-zoom a bit around just the path
    margin = 0.2
    ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
    ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)

    ax.set_title("Safest path animation (risk‑aware)", color="white")

    def update(frame):
        # move point
        point.set_data([x_coords[frame]], [y_coords[frame]])
        # extend trail
        trail.set_data(x_coords[: frame + 1], y_coords[: frame + 1])
        return point, trail

    ani = FuncAnimation(
        fig,
        update,
        frames=len(path),
        interval=600,   # ms between steps
        blit=True,
        repeat=False,
    )

    plt.show()


def ask_user_and_run():
    root = tk.Tk()
    root.title("RESQ OS - Choose Source & Target")

    tk.Label(root, text="Source junction:").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(root, text="Target junction:").grid(row=1, column=0, padx=10, pady=10)

    junction_names = list(JUNCTIONS.keys())

    source_var = tk.StringVar(value=junction_names[0])
    target_var = tk.StringVar(value=junction_names[1])

    source_cb = ttk.Combobox(
        root,
        textvariable=source_var,
        values=junction_names,
        state="readonly",
        width=35,
    )
    target_cb = ttk.Combobox(
        root,
        textvariable=target_var,
        values=junction_names,
        state="readonly",
        width=35,
    )

    source_cb.grid(row=0, column=1, padx=10, pady=10)
    target_cb.grid(row=1, column=1, padx=10, pady=10)

    def on_start():
        s_name = source_var.get()
        t_name = target_var.get()
        if s_name == t_name:
            return  # optional: show a warning instead

        source_id = JUNCTIONS[s_name]
        target_id = JUNCTIONS[t_name]

        root.destroy()
        run_animation(source_id, target_id)

    start_btn = tk.Button(root, text="Show Safest Path", command=on_start)
    start_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

    root.mainloop()


if __name__ == "__main__":
    ask_user_and_run()
