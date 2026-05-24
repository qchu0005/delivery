from flask import Flask, request, jsonify
from db import (
    get_all_locations, get_location,
    get_depot, create_delivery, get_delivery, update_delivery_arrived
)
from graph import build_graph, dijkstra

app = Flask(__name__)


# GET route

@app.route("/route", methods=["GET"])
def route():
    from_str = request.args.get("from")
    to_str = request.args.get("to")

    if from_str is None or to_str is None:
        return jsonify({"error": "Missing required query parameters: 'from' and 'to'"}), 400

    try:
        from_id = int(from_str)
        to_id = int(to_str)
    except ValueError:
        return jsonify({"error": "'from' and 'to' must be valid integers"}), 400

    from_loc = get_location(from_id)
    to_loc = get_location(to_id)

    if not from_loc:
        return jsonify({"error": f"Location with id {from_id} not found"}), 404
    if not to_loc:
        return jsonify({"error": f"Location with id {to_id} not found"}), 404

    graph = build_graph()
    path_ids, total_distance = dijkstra(graph, from_id, to_id)

    if path_ids is None:
        return jsonify({
            "from": {"id": from_loc["id"], "name": from_loc["name"]},
            "to":   {"id": to_loc["id"],   "name": to_loc["name"]},
            "path": [],
            "total_distance_km": None,
            "reachable": False,
        })

    path = [{"id": loc_id, "name": get_location(loc_id)["name"]} for loc_id in path_ids]

    return jsonify({
        "from": {"id": from_loc["id"], "name": from_loc["name"]},
        "to":   {"id": to_loc["id"],   "name": to_loc["name"]},
        "path": path,
        "total_distance_km": total_distance,
        "reachable": True,
    })



# GET locations

@app.route("/locations", methods=["GET"])
def locations():
    return jsonify(get_all_locations())


# POST deliveries

@app.route("/deliveries", methods=["POST"])
def post_delivery():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    customer_id = body.get("customer_id")
    truck_plate = body.get("truck_plate")

    if customer_id is None or not isinstance(customer_id, int):
        return jsonify({"error": "customer_id must be an integer"}), 400
    if not truck_plate or not isinstance(truck_plate, str) or not truck_plate.strip():
        return jsonify({"error": "truck_plate must be a non-empty string"}), 400

    location = get_location(customer_id)
    if not location:
        return jsonify({"error": f"Location with id {customer_id} not found"}), 400
    if location["type"] != "customer":
        return jsonify({"error": "customer_id must refer to a customer location, not a depot"}), 400

    depot = get_depot()
    graph = build_graph()
    path_ids, _ = dijkstra(graph, depot["id"], customer_id)
    if path_ids is None:
        return jsonify({"error": f"Customer location {customer_id} is not reachable from the depot"}), 400

    delivery = create_delivery(customer_id, truck_plate.strip())
    return jsonify(delivery), 201


# PATCH /deliveries/<id>/status 

@app.route("/deliveries/<int:delivery_id>/status", methods=["PATCH"])
def patch_delivery_status(delivery_id):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    new_status = body.get("status")
    if new_status not in ("arrived", "departed"):
        return jsonify({"error": "status must be 'arrived' or 'departed'"}), 422

    delivery = get_delivery(delivery_id)
    if not delivery:
        return jsonify({"error": f"Delivery with id {delivery_id} not found"}), 404

    current_status = delivery["status"]

    if current_status == "arrived":
        return jsonify({"error": "Delivery has already arrived; no further status changes allowed"}), 422
    if new_status == "departed":
        return jsonify({"error": "Invalid transition: delivery is already in 'departed' state"}), 422

    updated = update_delivery_arrived(delivery_id)
    return jsonify(updated)


