import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "delivery.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


#Locations

def get_all_locations():
    with _connect() as conn:
        rows = conn.execute("""
            SELECT l.id, l.name, l.type,
                   COUNT(r.id) AS road_count
            FROM locations l
            LEFT JOIN roads r ON r.from_id = l.id OR r.to_id = l.id
            GROUP BY l.id
            ORDER BY l.id
        """).fetchall()
    return [dict(row) for row in rows]


def get_location(location_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, name, type FROM locations WHERE id = ?",
            (location_id,)
        ).fetchone()
    return dict(row) if row else None


#Roads

def get_roads():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, from_id, to_id, distance_km, travel_time_min FROM roads"
        ).fetchall()
    return [dict(row) for row in rows]


#Task 4

#Depots
def get_depot():
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, name, type FROM locations WHERE type = 'depot' LIMIT 1"
        ).fetchone()
    return dict(row) if row else None

#Deliveries
def create_delivery(customer_id, truck_plate):
    with _connect() as conn:
        cursor = conn.execute(
            """INSERT INTO deliveries (customer_id, truck_plate, status, departed_at)
               VALUES (?, ?, 'departed', datetime('now'))""",
            (customer_id, truck_plate)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()
    return dict(row)

def get_delivery(delivery_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?",
            (delivery_id,)
        ).fetchone()
    return dict(row) if row else None


def update_delivery_arrived(delivery_id):
    with _connect() as conn:
        conn.execute(
            """UPDATE deliveries
               SET status = 'arrived', arrived_at = datetime('now')
               WHERE id = ?""",
            (delivery_id,)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?",
            (delivery_id,)
        ).fetchone()
    return dict(row)


def get_deliveries_summary():
    with _connect() as conn:
        rows = conn.execute("""
            SELECT
                l.id          AS customer_id,
                l.name        AS customer_name,
                COUNT(d.id)   AS total_deliveries,
                MAX(d.departed_at) AS last_delivery_date
            FROM locations l
            LEFT JOIN deliveries d ON d.customer_id = l.id
            WHERE l.type = 'customer'
            GROUP BY l.id, l.name
            ORDER BY l.id
        """).fetchall()
    return [dict(row) for row in rows]
