## Setup & Running

```bash
# 1. Install Flask
pip install Flask

# 2. Start the server (default port 5000)
python app.py
```

The server runs at `http://localhost:5000`.

## Language & Framework

**Python 3** with **Flask**.

Python chosen as it has built in standard library (sqlite3) and has cleaner syntax compared to JS (easier for DSA). Flask was chosen as it provides clean routing and JSON responses.

## How the Algorithm Works

The road network is modelled as an **undirected weighted graph** stored as an adjacency list in memory:

- Each location is a **node**.
- Each road is a **bidirectional edge** weighted by `distance_km`.

**Shortest path** uses **Dijkstra's algorithm** (min-heap / priority queue):

1. Start at the depot. Assign it distance 0; all other nodes get distance ∞.
2. Pop the lowest-distance unvisited node from the heap.
3. For each neighbouring node, compute `current_distance + edge_weight`. If that beats the previously known distance, update it and push to the heap.
4. Stop once the target node is popped.
5. Reconstruct the path by back-tracking through a `prev` pointer map.

If the target is never reached (distance stays ∞), the two locations are in disconnected components — the customer is unreachable.

**Reachability check** (Task 5) uses a simple depth-first search from the depot. Any customer node not visited by the DFS is unreachable, even if it has roads that only connect to other isolated nodes.

## API Endpoints

### GET /locations

Returns all locations with type and direct road connection count.

```bash
curl http://localhost:5000/locations
```

### GET /locations/unreachable _(Task 5)_

Returns customer locations that have no road path to the depot (determined via graph traversal, not just SQL).

```bash
curl http://localhost:5000/locations/unreachable
```

### GET /route?from=\<id\>&to=\<id\>

Finds the shortest path by distance between two locations. Returns `reachable: false` (HTTP 200) if no path exists. Returns HTTP 404 if either location ID is unknown, HTTP 400 if parameters are missing or non-integer.

```bash
# Happy path: depot → Petronas Cyberjaya
curl "http://localhost:5000/route?from=1&to=7"

# Unreachable customer
curl "http://localhost:5000/route?from=1&to=11"
```

### POST /deliveries

Logs a new delivery departure. Validates that the customer exists, is a customer (not depot), and is reachable from the depot.

```bash
curl -X POST http://localhost:5000/deliveries \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 7, "truck_plate": "WB5678C"}'
```

### PATCH /deliveries/\<id\>/status

Marks a delivery as arrived. Only the `departed → arrived` transition is valid; any other attempt returns HTTP 422.

```bash
curl -X PATCH http://localhost:5000/deliveries/7/status \
  -H "Content-Type: application/json" \
  -d '{"status": "arrived"}'
```

### GET /deliveries/summary _(Task 6)_

Returns per-customer delivery count and most recent delivery date, computed via a single SQL aggregation query.

```bash
curl http://localhost:5000/deliveries/summary
```

---

OR POSTMAN

GET http://localhost:5000/locations  
GET http://localhost:5000/locations/unreachable
GET http://localhost:5000/route?from=1&to=7
GET http://localhost:5000/route?from=1&to=11
POST http://localhost:5000/deliveries
PATCH http://localhost:5000/deliveries/1/status
GET http://localhost:5000/deliveries/summary

POST:
{
"customer_id": 7,
"truck_plate": "WB5678C"
}

PATCH:
{
"status": "arrived"
}

## Assumptions & Notes

- **Roads are bidirectional**: a `roads` row `(from_id=A, to_id=B)` allows travel in both directions. The graph builder adds both `A→B` and `B→A` edges.
- **Isolated nodes**: Locations 11 and 12 (Kerteh Terminal and Gebeng Industrial Hub) are connected to each other via a road but have no path to the depot. Both are correctly reported as unreachable by the graph traversal.
- **Shortest path metric**: distance in kilometres (`distance_km`). The `travel_time_min` column is stored in the DB but not used for routing, as the spec defines shortest path by distance.
- **Status transitions**: only `departed → arrived` is allowed. Once a delivery is marked arrived it is terminal.
