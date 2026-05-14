from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import threading

from karachi_assignment_graph import NODES, GRAPH
from search_algorithms import BFS, DFS, UCS, Greedy, AStar, IDAStar
from heuristics import h1_geographic, h2_karachi_informed, haversine_km
from karachi_real_graph import init_real_graph, get_nearest_node, REAL_GRAPH, REAL_NODES

app = FastAPI(title="Karachi Smart Transport Planner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aai-assignment-transportplan.web.app",
        "https://aai-assignment-transportplan.firebaseapp.com",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssignmentRequest(BaseModel):
    start: str
    goal: str
    algorithm: str
    heuristic: Optional[str] = None

class LocalSearchRequest(BaseModel):
    k_stops: int = 10

class RealRequest(BaseModel):
    source_lat: float
    source_lon: float
    dest_lat: float
    dest_lon: float
    algorithm: str
    heuristic: Optional[str] = None
    speed_kmh: Optional[float] = 25.0

@app.on_event("startup")
def startup_event():
    threading.Thread(target=init_real_graph, daemon=True).start()

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/assignment/nodes")
def get_assignment_nodes():
    return list(NODES.keys())

@app.post("/assignment/route")
def assignment_route(req: AssignmentRequest):
    if req.start not in NODES or req.goal not in NODES:
        raise HTTPException(status_code=400, detail="Invalid start or goal node")

    def get_h(node):
        if req.heuristic == "h2":
            return h2_karachi_informed(node, req.goal, NODES)
        return h1_geographic(node, req.goal, NODES)

    algo = req.algorithm.upper()
    if algo == "BFS":
        path, cost, exp, max_f = BFS(GRAPH, req.start, req.goal)
    elif algo == "DFS":
        path, cost, exp, max_f = DFS(GRAPH, req.start, req.goal)
    elif algo == "UCS":
        path, cost, exp, max_f = UCS(GRAPH, req.start, req.goal)
    elif algo == "GREEDY":
        path, cost, exp, max_f = Greedy(GRAPH, req.start, req.goal, get_h)
    elif algo in ["A*", "ASTAR"]:
        path, cost, exp, max_f = AStar(GRAPH, req.start, req.goal, get_h)
    elif algo in ["IDA*", "IDASTAR"]:
        path, cost, exp, max_f = IDAStar(GRAPH, req.start, req.goal, get_h)
    else:
        raise HTTPException(status_code=400, detail="Invalid algorithm")

    return {
        "mode": "assignment",
        "path": path,
        "cost_minutes": round(cost, 2),
        "nodes_expanded": exp,
        "max_frontier": max_f,
        "algorithm": req.algorithm,
        "heuristic": req.heuristic
    }

@app.post("/real/route")
def real_route(req: RealRequest):
    if REAL_GRAPH is None:
        raise HTTPException(status_code=503, detail="Graph is still initializing. Try again shortly.")

    src_node = get_nearest_node(req.source_lat, req.source_lon)
    dst_node = get_nearest_node(req.dest_lat, req.dest_lon)

    def get_h(node):
        if req.heuristic == "h2":
            return h2_karachi_informed(node, dst_node, REAL_NODES, req.speed_kmh)
        return h1_geographic(node, dst_node, REAL_NODES, req.speed_kmh)

    algo = req.algorithm.upper()
    if algo == "UCS":
        path, cost, exp, max_f = UCS(REAL_GRAPH, src_node, dst_node)
    elif algo == "GREEDY":
        path, cost, exp, max_f = Greedy(REAL_GRAPH, src_node, dst_node, get_h)
    elif algo in ["A*", "ASTAR"]:
        path, cost, exp, max_f = AStar(REAL_GRAPH, src_node, dst_node, get_h)
    elif algo in ["IDA*", "IDASTAR"]:
        path, cost, exp, max_f = IDAStar(REAL_GRAPH, src_node, dst_node, get_h)
    else:
        path, cost, exp, max_f = AStar(REAL_GRAPH, src_node, dst_node, get_h)

    path_latlon = []
    dist_km = 0.0
    for i in range(len(path)):
        lat, lon = REAL_NODES[path[i]]
        path_latlon.append([lat, lon])
        if i > 0:
            plat, plon = REAL_NODES[path[i - 1]]
            dist_km += haversine_km(plat, plon, lat, lon)

    constant_time = dist_km / (req.speed_kmh / 60.0) if req.speed_kmh else cost

    return {
        "mode": "real",
        "path_latlon": path_latlon,
        "distance_km": round(dist_km, 2),
        "graph_time_minutes": round(cost, 2),
        "constant_speed_minutes": round(constant_time, 2),
        "nodes_expanded": exp,
        "max_frontier": max_f,
        "algorithm": req.algorithm,
        "heuristic": req.heuristic
    }

@app.post("/assignment/local_search_optimize")
def local_search_optimize(req: LocalSearchRequest):
    from local_search import simulated_annealing, ALL_NODES, GRAPH

    best_stops, best_conns, best_val, history = simulated_annealing(
        GRAPH, ALL_NODES, k=req.k_stops, cooling=0.99
    )

    return {
        "mode": "optimizer",
        "best_stops": best_stops,
        "best_connections": best_conns,
        "objective": round(best_val, 4),
        "history": [round(v, 4) for v in history]
    }
