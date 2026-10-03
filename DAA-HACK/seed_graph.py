#!/usr/bin/env python3
"""Seed script for CodeBlue Nav graph database."""

import sqlite3
import os

NODES = [
    {"id": "N01", "label": "Central Station", "x": 100, "y": 100, "type": "start"},
    {"id": "N02", "label": "ER", "x": 200, "y": 150, "type": "er"},
    {"id": "N03", "label": "ICU", "x": 300, "y": 150, "type": "er"},
    {"id": "N04", "label": "Ward 4A", "x": 400, "y": 100, "type": "ward"},
    {"id": "N05", "label": "Ward 4B", "x": 500, "y": 150, "type": "ward"},
    {"id": "N06", "label": "Imaging", "x": 600, "y": 100, "type": "ward"},
    {"id": "N07", "label": "Pharmacy", "x": 700, "y": 150, "type": "ward"},
    {"id": "N08", "label": "Stairwell A", "x": 800, "y": 100, "type": "junction"},
    {"id": "N09", "label": "East Wing Junction", "x": 900, "y": 150, "type": "junction"},
    {"id": "N10", "label": "OR Block", "x": 1000, "y": 150, "type": "er"},
    {"id": "N11", "label": "Lab", "x": 200, "y": 300, "type": "ward"},
    {"id": "N12", "label": "Radiology", "x": 500, "y": 300, "type": "ward"},
    {"id": "N13", "label": "Lobby", "x": 800, "y": 300, "type": "start"},
    {"id": "N14", "label": "Corridor C Midpoint", "x": 600, "y": 350, "type": "junction"},
]

EDGES = [
    ("E01", "N01", "N02", 45, "Station-ER"),
    ("E02", "N01", "N03", 55, "Station-ICU"),
    ("E03", "N02", "N04", 30, "ER-W4A"),
    ("E04", "N03", "N05", 35, "ICU-W4B"),
    ("E05", "N04", "N05", 25, "W4A-W4B"),
    ("E06", "N05", "N06", 40, "W4B-Imaging"),
    ("E07", "N06", "N07", 30, "Imaging-Pharmacy"),
    ("E08", "N07", "N09", 35, "Pharmacy-EWJ"),
    ("E09", "N09", "N10", 45, "EWJ-ORBlock"),
    ("E10", "N10", "N11", 25, "ORBlock-Lab"),
    ("E11", "N11", "N12", 35, "Lab-Radiology"),
    ("E12", "N12", "N13", 50, "Radiology-Lobby"),
    ("E13", "N13", "N14", 20, "Lobby-CorridorC"),
    ("E14", "N14", "N06", 25, "CorridorC-Imaging"),
    ("E15", "N02", "N11", 70, "ER-Lab"),
    ("E16", "N03", "N12", 65, "ICU-Radiology"),
    ("E17", "N04", "N07", 80, "W4A-Pharmacy"),
    ("E18", "N05", "N13", 75, "W4B-Lobby"),
    ("E19", "N08", "N09", 15, "Stairwell-EWJ"),
    ("E20", "N08", "N13", 60, "Stairwell-Lobby"),
    ("E21", "N14", "N10", 30, "CorridorC-ORBlock"),
    ("E22", "N09", "N13", 30, "EWJ-Lobby"),
]

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital_graph.db")


def reset_db():
    """Drop and rebuild the SQLite database with fresh seed data."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id TEXT PRIMARY KEY,
            node_a TEXT NOT NULL,
            node_b TEXT NOT NULL,
            weight_seconds REAL NOT NULL,
            label TEXT NOT NULL,
            blocked INTEGER NOT NULL DEFAULT 0
        )
    """)
    for n in NODES:
        cur.execute(
            "INSERT INTO nodes (id, label, x, y, type) VALUES (?, ?, ?, ?, ?)",
            (n["id"], n["label"], n["x"], n["y"], n["type"]),
        )
    for e in EDGES:
        cur.execute(
            "INSERT INTO edges (id, node_a, node_b, weight_seconds, label, blocked) VALUES (?, ?, ?, ?, ?, ?)",
            (e[0], e[1], e[2], e[3], e[4], 0),
        )
    conn.commit()
    conn.close()
    print(f"Database seeded at {DB_PATH} with {len(NODES)} nodes and {len(EDGES)} edges.")


def get_adjacency_list(blocked_edges=None):
    """Return adjacency dict {node_id: [(neighbor, weight, label)]} respecting blocked edges."""
    if blocked_edges is None:
        blocked_edges = set()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Build placeholders for blocked edges
    placeholders = ",".join("?" for _ in blocked_edges)
    cur.execute(
        f"SELECT id, node_a, node_b, weight_seconds, label FROM edges WHERE blocked = 0 AND id NOT IN ({placeholders})",
        list(blocked_edges),
    )
    rows = cur.fetchall()

    adj = {n["id"]: [] for n in NODES}

    for edge_id, a, b, w, label in rows:
        adj[a].append((b, w, label))
        adj[b].append((a, w, label))

    conn.close()
    return adj


def print_adjacency(blocked_edges=None):
    """Print adjacency list for verification."""
    adj = get_adjacency_list(blocked_edges)
    for node in sorted(adj.keys()):
        nbrs = ", ".join(f"{n}({w}s)" for n, w, _ in adj[node])
        print(f"  {node} -> [{nbrs}]")


if __name__ == "__main__":
    reset_db()
    print("Adjacency list (all edges unblocked):")
    print_adjacency()
    print("\nAdjacency list (with Corridor C blocked: E13, E14):")
    print_adjacency(blocked_edges={"E13", "E14"})