NODES = {
    "Saddar": (24.8580, 67.0180),
    "Clifton": (24.8250, 67.0340),
    "DHA": (24.8050, 67.0450),
    "Korangi": (24.8190, 67.1140),
    "Malir": (24.8960, 67.1930),
    "Gulshan": (24.9180, 67.0970),
    "Johar": (24.9130, 67.1350),
    "North Nazimabad": (24.9370, 67.0430),
    "Orangi": (24.9450, 66.9980),
    "SITE": (24.9040, 66.9950),
    "Lyari": (24.8680, 66.9940),
    "Keamari": (24.8180, 66.9790),
    "Shah Faisal": (24.8820, 67.1470),
    "Landhi": (24.8360, 67.1650),
    "Baldia": (24.9460, 66.9630),
    "Gadap": (25.0200, 67.1260),
    "Bin Qasim": (24.7890, 67.3390),
    "Tariq Road": (24.8720, 67.0580),
    "Defence View": (24.8310, 67.0680),
    "Nazimabad": (24.9080, 67.0310)
}

EDGES = [
    # Your original 27 edges (unchanged)
    ("Saddar", "Clifton", 10),
    ("Saddar", "Tariq Road", 15),
    ("Saddar", "Lyari", 12),
    ("Clifton", "DHA", 10),
    ("Clifton", "Defence View", 15),
    ("DHA", "Korangi", 25), # Creek crossing bottleneck
    ("Korangi", "Landhi", 15),
    ("Korangi", "Defence View", 10),
    ("Defence View", "Tariq Road", 12),
    ("Tariq Road", "Gulshan", 20),
    ("Gulshan", "Johar", 10),
    ("Johar", "Shah Faisal", 15),
    ("Shah Faisal", "Malir", 15),
    ("Malir", "Landhi", 20),
    ("Gulshan", "North Nazimabad", 15),
    ("North Nazimabad", "Nazimabad", 10),
    ("Nazimabad", "SITE", 15),
    ("Nazimabad", "Saddar", 20),
    ("SITE", "Orangi", 12),
    ("SITE", "Baldia", 15),
    ("Orangi", "Baldia", 10),
    ("Lyari", "Keamari", 15),
    ("Keamari", "Clifton", 25),
    ("Gadap", "Malir", 30),
    ("Gadap", "Gulshan", 35),
    ("Bin Qasim", "Landhi", 25),
    ("Orangi", "North Nazimabad", 20),
    ("DHA", "Orangi", 55), # Cross city bottleneck
]

def build_graph():
    graph = {node: {} for node in NODES}
    for u, v, w in EDGES:
        graph[u][v] = w
        graph[v][u] = w
    return graph

GRAPH = build_graph()
