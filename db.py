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
            SELECT l.id, l.name, l.type
            FROM locations l
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


