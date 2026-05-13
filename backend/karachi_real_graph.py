import osmnx as ox
import networkx as nx
from scipy.spatial import KDTree
import numpy as np

REAL_GRAPH = None
REAL_NODES = {}
kd_tree = None
node_ids = []

def init_real_graph():
    global REAL_GRAPH, REAL_NODES, kd_tree, node_ids
    if REAL_GRAPH is not None: return
    
    print("Downloading OSM Data for Karachi (Simplified Bounding Box)...")
    # Central Karachi BBox to keep it lightweight.
    north, south, east, west = 24.95, 24.80, 67.15, 66.95
    
    try:
        try:
            # OSMnx 2.0+ expects bbox=(left, bottom, right, top) which is (west, south, east, north)
            G = ox.graph_from_bbox(bbox=(west, south, east, north), network_type='drive', simplify=True)
        except TypeError:
            # Fallback for older osmnx versions expecting (north, south, east, west)
            G = ox.graph_from_bbox(north, south, east, west, network_type='drive', simplify=True)
        
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        
        REAL_GRAPH = {}
        REAL_NODES = {}
        node_coords = []
        
        for node, data in G.nodes(data=True):
            REAL_NODES[node] = (data['y'], data['x'])
            node_coords.append([data['y'], data['x']])
            node_ids.append(node)
            REAL_GRAPH[node] = {}
            
        for u, v, key, data in G.edges(keys=True, data=True):
            tt_minutes = data.get('travel_time', 60) / 60.0
            if v in REAL_GRAPH[u]:
                REAL_GRAPH[u][v] = min(REAL_GRAPH[u][v], tt_minutes)
            else:
                REAL_GRAPH[u][v] = tt_minutes
                
        kd_tree = KDTree(np.array(node_coords))
        print(f"Real graph initialized successfully with {len(REAL_NODES)} nodes.")
    except Exception as e:
        import traceback
        print(f"ERROR INITIALIZING REAL GRAPH: {e}")
        traceback.print_exc()

def get_nearest_node(lat, lon):
    if kd_tree is None: init_real_graph()
    _, idx = kd_tree.query([lat, lon])
    return node_ids[idx]
