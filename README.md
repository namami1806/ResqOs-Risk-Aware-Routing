# ResQOS – Risk-Aware Evacuation Routing (T. Nagar, Chennai)

This repository presents a Python-based prototype of ResQOS, an AI-driven disaster evacuation system designed to compute risk-aware routes in urban environments like T. Nagar, Chennai. The system integrates real-world map data with multi-hazard inputs to generate safer evacuation paths.

⸻

Key Features
	•	Extracts drivable road networks from OpenStreetMap using OSMnx
	•	Integrates multi-hazard factors (water level, crowd density, rainfall, light conditions)
	•	Computes fuzzy risk scores for each road segment and derives effective routing cost
	•	Implements risk-aware shortest path routing using NetworkX
	•	Visualizes optimal evacuation paths (static and animated) using Matplotlib
	•	Provides a simple GUI (Tkinter) for interactive source-target selection

⸻

Team Contributions
	•	Prashanta Sarmah Bordoloi
	•	Developed core routing pipeline using OSMnx and NetworkX
	•	Implemented fuzzy risk scoring and cost computation
	•	Built visualization modules and GUI interface
	•	Namami Chouhan
	•	Implemented and analyzed ML/DL models (Autoencoders, Isolation Forest, GNNs)
	•	Performed comparative evaluation using graphical analysis
	•	Contributed to system design and data processing workflow (ongoing)

⸻

Tech Stack
	•	Python
	•	OSMnx, NetworkX, pandas, NumPy
	•	Matplotlib (visualization & animation)
	•	Tkinter (GUI)
	•	Machine Learning / Deep Learning models

⸻

How to Run (Outline)
	1.	Run get_tnagar_graph.py to download and store the road network
	2.	Run build_edges_with_risk.py to compute risk scores and costs
	3.	Run run_safe_path.py for routing
	4.	Run animate_safe_path.py for interactive visualization