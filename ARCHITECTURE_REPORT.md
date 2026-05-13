# Architecture and Technical Report
## Karachi Smart Transport Planner

### 1. Project Overview
This project implements intelligent routing algorithms over two representations of Karachi's transport network:
1. **Assignment Graph**: A simplified, abstract graph with 20 static nodes representing major districts.
2. **Real OSM Graph**: A concrete, highly detailed mapping of exact roads downloaded directly from OpenStreetMap servers.

### 2. Backend Architecture (Python & FastAPI)
The backend is completely stateless and computation-heavy.
- **FastAPI Core**: Handles routing API requests via `routing_api.py`. It starts an asynchronous daemon thread on startup to pull OSM data.
- **Algorithms Module**: `search_algorithms.py` implements pure AI algorithms:
  - `BFS / DFS`: Uninformed searches, exploring uniformly or deeply.
  - `UCS (Dijkstra)`: Explores uniformly but respects edge weights (travel times).
  - `Greedy Best-First`: Ignores distance traveled and aggressively prioritizes nodes appearing closer to the goal geographically.
  - `A*`: Balances distance traveled so far (`g`) and estimated distance remaining (`h`) to guarantee optimal paths efficiently.
  - `IDA*`: Memory-bounded A* that uses iterative deepening to strictly limit the frontier memory size.
- **OSMnx Integration**: In `karachi_real_graph.py`, `OSMnx` converts bounding box coordinates into a strictly drivable network (`networkx` MultiDiGraph). A `SciPy KDTree` is used to index all intersection coordinates so that when a user taps a random point on the map, it instantly maps (snaps) to the closest valid street intersection.

### 3. Frontend Architecture (Flutter)
The frontend relies heavily on reactivity:
- **State Management**: Uses simple `setState` bound to API asynchronous `Future` completions.
- **Map Layer**: `flutter_map` utilizes `tile.openstreetmap.org` for real-time map rendering.
- **Location Search**: Integrates `nominatim.openstreetmap.org` to allow users to search for locations using text instead of just tapping manually.

### 4. Working Flow & Data Flow
1. **User interaction**: User opens the Flutter App, selects Real Mode.
2. **Search API**: User types "Saddar", the app asks Nominatim API for exact latitude/longitude, and pans the map.
3. **Routing API**: User clicks "Find Route". The app posts coordinates to `http://localhost:8000/real/route`.
4. **Backend Processing**:
   - Backend queries the `KDTree` to find the closest road nodes.
   - Triggers the selected algorithm (e.g., A*).
   - Generates the path and converts node IDs back into Lat/Lon arrays.
5. **Visualization**: Flutter map draws a polyline connecting the returned Lat/Lon array.

### 5. Why the Graph Initializing Delay?
When the backend boots up, it fetches thousands of nodes and edges representing every single street in central Karachi from an external server over the internet. This is done asynchronously to allow the server to start immediately. However, if the user requests a route before this download finishes, the API politely blocks the request and instructs the app to show a "still initializing" message.
