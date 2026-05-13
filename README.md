# Karachi Smart Transport Planner

This project is a complete system containing a Python backend API and a Flutter Mobile/Web frontend, designed to perform advanced graph search routing algorithms on the road networks of Karachi.

## System Architecture

The project is split into two layers:
1. **FastAPI Backend (`backend/`)**: Handles memory-intensive graph loading and executes search algorithms (`A*`, `Greedy`, `UCS`, `BFS`, `DFS`, `IDA*`).
2. **Flutter Frontend (`karachi_transport_app/`)**: Provides an interactive, Map-based user interface to visualize routing results.

### Features
- **Assignment Mode**: A fixed graph of 20 popular locations in Karachi with pre-defined connections.
- **Real Mode**: Dynamically downloads the actual OpenStreetMap drivable network of central Karachi using `OSMnx` and computes realistic paths using actual latitude and longitude.

---

## 🚀 How to Run

### 1. Run the Backend
Navigate to the `backend` folder and execute the server:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn routing_api:app --reload --port 8000
```
- Wait for the console to output `Real graph initialized successfully`. This takes ~15 seconds while OpenStreetMap data downloads in the background.

### 2. Run the Frontend
Open a new terminal, navigate to the `karachi_transport_app` folder, and launch Flutter:
```bash
cd karachi_transport_app
flutter run
```

---

## 🔍 Understanding Heuristics (h1 & h2)

In Artificial Intelligence Search algorithms (like `A*` and `Greedy Best-First`), a **heuristic** is a rule-of-thumb estimate of how far a node is from the goal. 
For an algorithm like A* to guarantee the shortest path, the heuristic must be **admissible** (it must never overestimate the actual cost).

### What is `h1`?
`h1` is the **Geographic Straight-Line Distance** heuristic. 
It calculates the direct "bird-flight" distance between the current node and the goal node using the Haversine formula on their Latitude and Longitude. It then divides this distance by an average driving speed (e.g., 25km/h) to get a time estimate in minutes. 
Because a straight line is the shortest possible physical distance, it will naturally never overestimate the real driving time, making it strictly admissible.

### What is `h2`?
`h2` is an **Informed Karachi-Specific** heuristic. 
It extends the intuition of `h1` by making assumptions about real-world conditions (e.g., North-South traffic in Karachi is often heavily penalized compared to East-West traffic due to specific road architectures and bottlenecks like bridges). However, to guarantee it remains mathematically admissible, we adjust the assumed max speed safely (e.g., 35km/h). This results in a tighter bound than `h1` which can sometimes result in expanding slightly fewer nodes while still finding the optimal path.
