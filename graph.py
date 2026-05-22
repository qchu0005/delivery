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


