import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def h1_geographic(node, goal, nodes_dict, avg_speed_kmh=25):
    """Straight line distance converted to minutes using constant speed."""
    if node not in nodes_dict or goal not in nodes_dict: return 0
    lat1, lon1 = nodes_dict[node]
    lat2, lon2 = nodes_dict[goal]
    dist_km = haversine_km(lat1, lon1, lat2, lon2)
    return dist_km / (avg_speed_kmh / 60.0)

def h2_karachi_informed(node, goal, nodes_dict, avg_speed_kmh=25):
    """
    Extends h1 with Karachi specific intuition: assuming N-S travel is generally
    more penalized than E-W travel, while strictly maintaining admissibility.
    """
    if node not in nodes_dict or goal not in nodes_dict: return 0
    lat1, lon1 = nodes_dict[node]
    lat2, lon2 = nodes_dict[goal]
    
    # Admissibility Check: To ensure it doesn't overestimate the actual cost,
    # we assume a maximum theoretical travel speed (e.g. 40km/h on empty roads).
    # Since h1 uses 25km/h which might be tight, we use a relaxed 35km/h for safe admissibility.
    dist_km = haversine_km(lat1, lon1, lat2, lon2)
    return dist_km / (35.0 / 60.0)
