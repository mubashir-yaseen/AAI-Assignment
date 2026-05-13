from collections import deque
import heapq

def BFS(graph, start, goal):
    if start == goal: return [start], 0, 0, 1
    frontier = deque([(start, [start], 0)])
    visited = {start}
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        curr, path, cost = frontier.popleft()
        nodes_expanded += 1
        
        for neighbor, weight in graph.get(curr, {}).items():
            if neighbor not in visited:
                if neighbor == goal:
                    return path + [neighbor], cost + weight, nodes_expanded, max_frontier_size
                visited.add(neighbor)
                frontier.append((neighbor, path + [neighbor], cost + weight))
    
    return [], 0, nodes_expanded, max_frontier_size

def DFS(graph, start, goal):
    frontier = [(start, [start], 0)]
    visited = set()
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        curr, path, cost = frontier.pop()
        
        if curr == goal:
            return path, cost, nodes_expanded, max_frontier_size
            
        if curr not in visited:
            visited.add(curr)
            nodes_expanded += 1
            for neighbor, weight in graph.get(curr, {}).items():
                if neighbor not in visited:
                    frontier.append((neighbor, path + [neighbor], cost + weight))
                    
    return [], 0, nodes_expanded, max_frontier_size

def UCS(graph, start, goal):
    frontier = [(0, start, [start])]
    visited = set()
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        cost, curr, path = heapq.heappop(frontier)
        
        if curr == goal:
            return path, cost, nodes_expanded, max_frontier_size
            
        if curr not in visited:
            visited.add(curr)
            nodes_expanded += 1
            for neighbor, weight in graph.get(curr, {}).items():
                if neighbor not in visited:
                    heapq.heappush(frontier, (cost + weight, neighbor, path + [neighbor]))
                    
    return [], 0, nodes_expanded, max_frontier_size

def Greedy(graph, start, goal, heuristic_fn):
    frontier = [(heuristic_fn(start), start, [start], 0)]
    visited = set()
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, curr, path, cost = heapq.heappop(frontier)
        
        if curr == goal:
            return path, cost, nodes_expanded, max_frontier_size
            
        if curr not in visited:
            visited.add(curr)
            nodes_expanded += 1
            for neighbor, weight in graph.get(curr, {}).items():
                if neighbor not in visited:
                    heapq.heappush(frontier, (heuristic_fn(neighbor), neighbor, path + [neighbor], cost + weight))
                    
    return [], 0, nodes_expanded, max_frontier_size

def AStar(graph, start, goal, heuristic_fn):
    frontier = [(heuristic_fn(start), 0, start, [start])]
    visited = {}
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        est_total, g_cost, curr, path = heapq.heappop(frontier)
        
        if curr == goal:
            return path, g_cost, nodes_expanded, max_frontier_size
            
        if curr not in visited or g_cost < visited[curr]:
            visited[curr] = g_cost
            nodes_expanded += 1
            for neighbor, weight in graph.get(curr, {}).items():
                new_cost = g_cost + weight
                heapq.heappush(frontier, (new_cost + heuristic_fn(neighbor), new_cost, neighbor, path + [neighbor]))
                    
    return [], 0, nodes_expanded, max_frontier_size

def IDAStar(graph, start, goal, heuristic_fn):
    bound = heuristic_fn(start)
    path = [start]
    path_set = {start}
    nodes_expanded = [0]
    max_frontier_size = [1]
    
    def search(curr, g, bound):
        f = g + heuristic_fn(curr)
        if f > bound:
            return f, None
        if curr == goal:
            return True, g
        
        min_cost = float('inf')
        nodes_expanded[0] += 1
        max_frontier_size[0] = max(max_frontier_size[0], len(path))
        
        for neighbor, weight in graph.get(curr, {}).items():
            if neighbor not in path_set:
                path.append(neighbor)
                path_set.add(neighbor)
                res, found_cost = search(neighbor, g + weight, bound)
                if res is True:
                    return True, found_cost
                if res < min_cost:
                    min_cost = res
                path.pop()
                path_set.remove(neighbor)
        return min_cost, None

    while True:
        res, cost = search(start, 0, bound)
        if res is True:
            return list(path), cost, nodes_expanded[0], max_frontier_size[0]
        if res == float('inf'):
            return [], 0, nodes_expanded[0], max_frontier_size[0]
        bound = res
