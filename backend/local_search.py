import random
import math
import os
import os
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from collections import defaultdict
from karachi_assignment_graph import NODES, GRAPH
from search_algorithms import UCS

ALL_NODES = list(NODES.keys())
K_STOPS = 10

def build_local_graph(connections, graph):
    local_graph = defaultdict(dict)
    for u, v in connections:
        if u in graph and v in graph[u]:
            local_graph[u][v] = graph[u][v]
            local_graph[v][u] = graph[v][u]
    return local_graph

def compute_objective(stops, connections, graph, all_nodes, alpha=0.5, beta=0.3, gamma=0.2):
    if not stops:
        return 0.0
    
    # 1. Coverage
    reachable = set(stops)
    for stop in stops:
        for neighbor in graph.get(stop, {}):
            reachable.add(neighbor)
    coverage = len(reachable) / len(all_nodes)
    
    # 2. Connectivity
    local_graph = build_local_graph(connections, graph)
    possible_pairs = len(stops) * (len(stops) - 1) / 2
    if possible_pairs == 0:
        return alpha * coverage
        
    connected_pairs = 0
    total_time = 0
    pairs_with_path = 0
    
    for i in range(len(stops)):
        for j in range(i+1, len(stops)):
            u, v = stops[i], stops[j]
            path, cost, _, _ = UCS(local_graph, u, v)
            if path:
                connected_pairs += 1
                total_time += cost
                pairs_with_path += 1
                
    connectivity = connected_pairs / possible_pairs
    
    # 3. Efficiency
    avg_time = total_time / pairs_with_path if pairs_with_path > 0 else 120.0
    efficiency = max(0.0, 1.0 - (avg_time / 120.0))
    
    return alpha * coverage + beta * connectivity + gamma * efficiency

def random_state(all_nodes, k, graph):
    stops = random.sample(all_nodes, k)
    connections = []
    # Add ALL valid direct edges between the chosen stops
    for i in range(len(stops)):
        for j in range(i+1, len(stops)):
            u, v = stops[i], stops[j]
            if v in graph.get(u, {}):
                connections.append((u, v))
    return stops, connections

def get_neighbours(stops, connections, graph, all_nodes):
    neighbours = []
    inactive = list(set(all_nodes) - set(stops))
    
    # Neighbour Type 1: Swap one stop
    if inactive:
        for _ in range(2):
            new_stops = stops.copy()
            idx = random.randint(0, len(new_stops)-1)
            new_stops[idx] = random.choice(inactive)
            
            new_conns = []
            for i in range(len(new_stops)):
                for j in range(i+1, len(new_stops)):
                    u, v = new_stops[i], new_stops[j]
                    if v in graph.get(u, {}):
                        new_conns.append((u, v))
            neighbours.append((new_stops, new_conns))
            
    # Neighbour Type 2: Remove a connection (to simulate adding/removing)
    if connections:
        new_conns = connections.copy()
        new_conns.pop(random.randint(0, len(new_conns)-1))
        neighbours.append((stops.copy(), new_conns))
        
    return neighbours

def hill_climbing(graph, all_nodes, k=10, max_steps=200, sideways=False):
    current_stops, current_conns = random_state(all_nodes, k, graph)
    current_obj = compute_objective(current_stops, current_conns, graph, all_nodes)
    
    sideways_count = 0
    steps_taken = 0
    
    for _ in range(max_steps):
        steps_taken += 1
        neighbours = get_neighbours(current_stops, current_conns, graph, all_nodes)
        
        best_n_stops, best_n_conns = None, None
        best_n_obj = -1
        
        for n_stops, n_conns in neighbours:
            obj = compute_objective(n_stops, n_conns, graph, all_nodes)
            if obj > best_n_obj:
                best_n_obj = obj
                best_n_stops, best_n_conns = n_stops, n_conns
                
        if best_n_obj > current_obj:
            current_stops, current_conns, current_obj = best_n_stops, best_n_conns, best_n_obj
            sideways_count = 0
        elif sideways and best_n_obj == current_obj and sideways_count < 20:
            current_stops, current_conns, current_obj = best_n_stops, best_n_conns, best_n_obj
            sideways_count += 1
        else:
            break
            
    return current_stops, current_conns, current_obj, steps_taken

def simulated_annealing(graph, all_nodes, k=10, T_init=100, cooling=0.95, max_steps=1000, T_min=0.01):
    current_stops, current_conns = random_state(all_nodes, k, graph)
    current_obj = compute_objective(current_stops, current_conns, graph, all_nodes)
    
    best_stops, best_conns, best_val = current_stops.copy(), current_conns.copy(), current_obj
    history = [current_obj]
    T = T_init
    
    for _ in range(max_steps):
        if T < T_min:
            break
            
        neighbours = get_neighbours(current_stops, current_conns, graph, all_nodes)
        if not neighbours:
            break
            
        n_stops, n_conns = random.choice(neighbours)
        n_obj = compute_objective(n_stops, n_conns, graph, all_nodes)
        
        delta = n_obj - current_obj
        if delta > 0 or random.random() < math.exp(delta / T):
            current_stops, current_conns, current_obj = n_stops, n_conns, n_obj
            
            if current_obj > best_val:
                best_val = current_obj
                best_stops, best_conns = current_stops.copy(), current_conns.copy()
                
        history.append(current_obj)
        T *= cooling
        
    return best_stops, best_conns, best_val, history

def plot_best_network(stops, connections, nodes_dict):
    if not MATPLOTLIB_AVAILABLE: return
    os.makedirs("./plots", exist_ok=True)
    plt.figure(figsize=(10, 8))
    
    # Plot all nodes lightly
    for node, (lat, lon) in nodes_dict.items():
        plt.scatter(lon, lat, c='lightgray', s=50)
        plt.text(lon, lat, node, fontsize=8, alpha=0.5)
        
    # Plot selected stops
    for stop in stops:
        lat, lon = nodes_dict[stop]
        plt.scatter(lon, lat, c='red', s=100, zorder=5)
        plt.text(lon, lat, stop, fontsize=10, fontweight='bold', zorder=6)
        
    # Plot connections
    for u, v in connections:
        if u in nodes_dict and v in nodes_dict:
            lat1, lon1 = nodes_dict[u]
            lat2, lon2 = nodes_dict[v]
            plt.plot([lon1, lon2], [lat1, lat2], 'b-', linewidth=2, zorder=4)
            
    plt.title("Best Transport Network (Layer 3)")
    plt.savefig("./plots/best_network.png")
    plt.close()

def plot_sa_cooling(sa_results):
    if not MATPLOTLIB_AVAILABLE: return
    os.makedirs("./plots", exist_ok=True)
    plt.figure(figsize=(10, 6))
    rates = list(sa_results.keys())
    avgs = [res['avg'] for res in sa_results.values()]
    maxs = [res['max'] for res in sa_results.values()]
    
    x = range(len(rates))
    plt.bar([i - 0.2 for i in x], avgs, width=0.4, label='Average Objective')
    plt.bar([i + 0.2 for i in x], maxs, width=0.4, label='Max Objective')
    
    plt.xticks(x, [f"Cooling={r}" for r in rates])
    plt.ylabel("Objective Value")
    plt.title("Simulated Annealing Performance by Cooling Rate")
    plt.legend()
    plt.savefig("./plots/sa_cooling.png")
    plt.close()

def plot_hc_comparison(hc_no_sw, hc_sw):
    if not MATPLOTLIB_AVAILABLE: return
    os.makedirs("./plots", exist_ok=True)
    plt.figure(figsize=(8, 6))
    labels = ['No Sideways', 'With Sideways']
    avgs = [hc_no_sw['avg'], hc_sw['avg']]
    maxs = [hc_no_sw['max'], hc_sw['max']]
    
    x = range(len(labels))
    plt.bar([i - 0.2 for i in x], avgs, width=0.4, label='Average')
    plt.bar([i + 0.2 for i in x], maxs, width=0.4, label='Max')
    
    plt.xticks(x, labels)
    plt.ylabel("Objective Value")
    plt.title("Hill Climbing: Sideways vs No Sideways Moves")
    plt.legend()
    plt.savefig("./plots/hc_comparison.png")
    plt.close()

def run_layer3_experiments(graph, all_nodes, runs=50):
    print("Running Layer 3 Experiments...")
    
    # 1. Hill Climbing (No sideways)
    hc_no_sw_vals = []
    for _ in range(runs):
        _, _, val, _ = hill_climbing(graph, all_nodes, k=K_STOPS, sideways=False)
        hc_no_sw_vals.append(val)
        
    hc_no_sw_stats = {
        'avg': sum(hc_no_sw_vals)/runs,
        'max': max(hc_no_sw_vals),
        'success_rate': sum(1 for v in hc_no_sw_vals if v > 0.5)/runs
    }
    
    # 2. Hill Climbing (With sideways)
    hc_sw_vals = []
    for _ in range(runs):
        _, _, val, _ = hill_climbing(graph, all_nodes, k=K_STOPS, sideways=True)
        hc_sw_vals.append(val)
        
    hc_sw_stats = {
        'avg': sum(hc_sw_vals)/runs,
        'max': max(hc_sw_vals),
        'success_rate': sum(1 for v in hc_sw_vals if v > 0.5)/runs
    }
    
    # 3. Simulated Annealing
    cooling_rates = [0.90, 0.95, 0.99]
    sa_results = {}
    best_overall_sa_val = -1
    best_overall_sa_stops = None
    best_overall_sa_conns = None
    
    for rate in cooling_rates:
        vals = []
        for _ in range(runs):
            stops, conns, val, _ = simulated_annealing(graph, all_nodes, k=K_STOPS, cooling=rate)
            vals.append(val)
            if val > best_overall_sa_val:
                best_overall_sa_val = val
                best_overall_sa_stops = stops
                best_overall_sa_conns = conns
                
        sa_results[rate] = {
            'avg': sum(vals)/runs,
            'max': max(vals),
            'success_rate': sum(1 for v in vals if v > 0.5)/runs
        }
        
    # Plotting
    plot_hc_comparison(hc_no_sw_stats, hc_sw_stats)
    plot_sa_cooling(sa_results)
    if best_overall_sa_stops:
        plot_best_network(best_overall_sa_stops, best_overall_sa_conns, NODES)
        
    # Print Summary
    print("-" * 50)
    print("EXPERIMENT RESULTS (50 runs each)")
    print("-" * 50)
    print(f"HC (No Sideways): Avg={hc_no_sw_stats['avg']:.3f}, Max={hc_no_sw_stats['max']:.3f}, Success(>0.5)={hc_no_sw_stats['success_rate']*100}%")
    print(f"HC (With Sideways): Avg={hc_sw_stats['avg']:.3f}, Max={hc_sw_stats['max']:.3f}, Success(>0.5)={hc_sw_stats['success_rate']*100}%")
    for rate in cooling_rates:
        st = sa_results[rate]
        print(f"SA (Cooling {rate}): Avg={st['avg']:.3f}, Max={st['max']:.3f}, Success(>0.5)={st['success_rate']*100}%")
    print("-" * 50)
    
    return {
        "hc_no_sideways": hc_no_sw_stats,
        "hc_sideways": hc_sw_stats,
        "sa_results": sa_results
    }

if __name__ == "__main__":
    run_layer3_experiments(GRAPH, ALL_NODES, runs=50)
