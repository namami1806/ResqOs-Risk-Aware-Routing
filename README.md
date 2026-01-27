# ResQOS – T. Nagar Risk-Aware Routing

This repository contains a Python prototype for **ResQOS**, a lightweight AI micro‑OS that computes risk‑aware routes in T. Nagar, Chennai.

## Features

- Download T. Nagar drivable road network from OpenStreetMap using OSMnx.
- Attach multi-hazard data (water level, crowd density, rainfall, light).
- Compute fuzzy risk scores per road segment and derive an effective cost.
- Run risk‑aware shortest path routing with NetworkX.
- Visualise the safest path using Matplotlib (static and animated).
- Simple Tkinter GUI to select source and target junctions.

## Tech stack

- Python
- OSMnx, NetworkX, pandas, NumPy
- Matplotlib (with FuncAnimation)
- Tkinter (GUI)

## How to run (outline)

1. Run `get_tnagar_graph.py` to download and save the T. Nagar graph.
2. Run `build_edges_with_risk.py` to compute risk scores and effective costs.
3. Run `run_safe_path.py` to compute a sample safest path.
4. Run `animate_safe_path.py` to select junctions and see the path animation.
