import heapq
from db import get_all_locations, get_roads


def build_graph():
    """Load all locations and roads from the DB into a bidirectional adjacency list."""
    graph = {loc["id"]: [] for loc in get_all_locations()}

    for road in get_roads():
        a, b, dist = road["from_id"], road["to_id"], road["distance_km"]
        graph[a].append((b, dist))
        graph[b].append((a, dist))

    return graph


def dijkstra(graph, start, end):
    """
    Find the shortest path by distance between two node IDs using Dijkstra's algorithm.

    Returns (path, total_distance_km) where path is a list of location IDs in order,
    or (None, None) if no path exists.
    """

    # If ID does not exist in the graph
    if start not in graph or end not in graph:
        return None, None

    # if already at destination, return early
    if start == end:
        return [start], 0.0

    # assume every node is infinite 
    #initialise other variables
    dist = {node: float("inf") for node in graph}
    dist[start] = 0.0
    prev = {node: None for node in graph} #previous node for reconstruction of path
    heap = [(0.0, start)]

    while heap:
        current_dist, current = heapq.heappop(heap)

        if current_dist > dist[current]:
            continue

        if current == end:
            break

        for neighbor, weight in graph[current]:
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    if dist[end] == float("inf"):
        return None, None

    # reconstruct the path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return path, round(dist[end], 2)


def reachable_from(graph, start):
    """Return the set of all node IDs reachable from start (inclusive)."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor, _ in graph.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
    return visited
