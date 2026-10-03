"""FastAPI skeleton for CodeBlue Nav.

Endpoints:
  GET  /graph          -> full node/edge list for the frontend
  POST /route          -> {src, dst, algo: "dijkstra"|"bfs"} -> {path, cost, stats}
  POST /simulate/block {edge_id} -> toggles edge blocked flag, recomputes routes
  POST /call {type, dst} -> creates call, computes route, returns re-ordered queue
  GET  /queue          -> current queue with each call's ETA and path
  POST /reset          -> restore all edges unblocked, clear active calls
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from typing import Set, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CodeBlue Nav API", description="Hospital emergency route engine")

# CORS open to localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory active calls list (for /simulate/block and /call endpoints)
active_calls: list[dict] = []

# Triage priority queue instance
from backend.app.triage.priority_queue import triage_queue, EmergencyCall, add_call, PriorityQueue


# ── Helper: get adjacency respecting blocked edges ────────────────────────

def _get_seed_module():
    """Lazy import to avoid circular import issues at module load time."""
    from backend.app.graph.seed import get_adjacency_list, reset_db
    return get_adjacency_list, reset_db


def _adj(blocked_edges: set | None = None):
    """Return adjacency dict respecting given blocked edge IDs."""
    get_adj, _ = _get_seed_module()
    if blocked_edges is None:
        blocked_edges = set()
    return get_adj(blocked_edges=blocked_edges)


# ── GET /graph ─────────────────────────────────────────────────────────────

@app.get("/graph", tags=["api"])
def get_graph() -> dict:
    """Return full node and edge list for the frontend."""
    import backend.app.graph.seed as seed_mod

    conn = None
    try:
        DB_PATH = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "hospital_graph.db",
        )
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT id, label, x, y, type FROM nodes")
        nodes = [
            {"id": row[0], "label": row[1], "x": row[2], "y": row[3], "type": row[4]}
            for row in cur.fetchall()
        ]

        cur.execute(
            "SELECT id, node_a, node_b, weight_seconds, label, blocked FROM edges"
        )
        edges = [
            {
                "id": row[0],
                "node_a": row[1],
                "node_b": row[2],
                "weight_seconds": row[3],
                "label": row[4],
                "blocked": bool(row[5]),
            }
            for row in cur.fetchall()
        ]

        return {"nodes": nodes, "edges": edges}
    finally:
        if conn:
            conn.close()


# ── POST /route ────────────────────────────────────────────────────────────

class RouteRequest(dict):
    """Request body for /route endpoint."""

    def __init__(self, src: str, dst: str, algo: str):
        super().__init__(src=src, dst=dst, algo=algo)


@app.post("/route", tags=["api"])
def calculate_route(src: str, dst: str, algo: str = "dijkstra") -> dict:
    """Compute a route from src to dst using the specified algorithm."""
    from backend.app.graph.dijkstra import dijkstra
    from backend.app.graph.bfs import bfs
    from backend.app.graph.dijkstra import NoPathError

    if algo not in ("dijkstra", "bfs"):
        raise HTTPException(status_code=422, detail="algo must be 'dijkstra' or 'bfs'")

    adj = _adj()  # no blocked edges by default
    blocked_edges: set = set()

    try:
        if algo == "dijkstra":
            path, cost, stats = dijkstra(adj, src, dst, blocked_edges)
        else:
            from backend.app.graph.bfs import bfs as bfs_func
            result = bfs_func(adj, src, dst, blocked_edges)
            path = result.path
            cost = result.cost
            stats = result.stats

        return {"path": path, "cost": cost, "stats": {
            "nodes_settled": stats.nodes_settled,
            "edges_relaxed": stats.edges_relaxed,
        }}
    except NoPathError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── POST /simulate/block ──────────────────────────────────────────────────

class BlockRequest(dict):
    """Request body for /simulate/block endpoint."""

    def __init__(self, edge_id: str):
        super().__init__(edge_id=edge_id)


@app.post("/simulate/block", tags=["api"])
def simulate_block(edge_id: str) -> dict:
    """Toggle an edge's blocked flag and recompute routes for active calls."""
    # Toggle blocked flag in DB
    DB_PATH = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "hospital_graph.db",
    )
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if edge exists and toggle its blocked status
    cur.execute("SELECT id, blocked FROM edges WHERE id = ?", (edge_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Edge {edge_id} not found")

    new_blocked = not bool(row[1])
    cur.execute("UPDATE edges SET blocked = ? WHERE id = ?", (1 if new_blocked else 0, edge_id))
    conn.commit()
    conn.close()

    # Recompute routes for all active calls
    adj_blocked = _adj(blocked_edges={edge_id})

    updated_routes = []
    for call in active_calls:
        call_dst = call["dst"]
        call_src = call["src"]
        call_algo = call.get("algo", "dijkstra")

        from backend.app.graph.dijkstra import dijkstra as dijkstra_func
        from backend.app.graph.bfs import bfs as bfs_func

        try:
            if call_algo == "dijkstra":
                path, cost, stats = dijkstra_func(adj_blocked, call_src, call_dst)
            else:
                result = bfs_func(adj_blocked, call_src, call_dst)
                path = result.path
                cost = result.cost
                stats = result.stats

            updated_routes.append({
                "call_id": call["id"],
                "dst": call_dst,
                "new_path": path,
                "new_cost": cost,
            })
        except NoPathError:
            # Mark as no viable route
            from backend.app.graph.dijkstra import NoPathError as NoPathError2
            updated_routes.append({
                "call_id": call["id"],
                "dst": call_dst,
                "new_path": None,
                "new_cost": None,
                "no_viable_route": True,
            })

    return {
        "edge_id": edge_id,
        "edge_blocked": new_blocked,
        "updated_routes": updated_routes,
    }


# ── POST /call ─────────────────────────────────────────────────────────────

class CallRequest(dict):
    """Request body for /call endpoint.

    Fields:
        type: call type (e.g., "Stroke Alert")
        dst: destination node ID (e.g., "N02")
    """

    def __init__(self, call_type: str, dst: str):
        super().__init__(type=call_type, dst=dst)


@app.post("/call", tags=["triage"])
def create_call(call_type: str, dst: str) -> dict:
    """Create a new emergency call, compute its route, and return the re-ordered queue.

    Request:
        type: call type (e.g., "Stroke Alert")
        dst: destination node ID (e.g., "N02")

    Response:
        {
            "call": {id, type, dst, severity, path, cost, eta},
            "queue": [
                {id, type, dst, severity, eta, path, cost},
                ...
            ]
        }
    """
    # Create the call and add to triage queue (severity 3 by default, can be overridden)
    call = add_call(call_type, dst, severity=3)

    # Compute route from N01 to dst using Dijkstra
    adj = _adj()
    from backend.app.graph.dijkstra import dijkstra, NoPathError

    try:
        path, cost, stats = dijkstra(adj, "N01", dst)
    except NoPathError:
        path, cost = [], 0.0

    # Update the call's path and cost
    call.path = path
    call.cost = cost
    call.eta = cost

    # Update ETA in the priority queue
    triage_queue.update_eta(call.id, cost)

    # Recompute routes for all active calls
    updated_routes = []
    for c in triage_queue.get_all():
        try:
            p, cost_val, _ = dijkstra(adj, "N01", c.dst)
            updated_routes.append({
                "id": c.id,
                "type": c.type,
                "dst": c.dst,
                "severity": c.severity,
                "eta": cost_val,
                "path": p,
            })
        except Exception:
            updated_routes.append({
                "id": c.id,
                "type": c.type,
                "dst": c.dst,
                "severity": c.severity,
                "eta": None,
                "path": None,
            })

    # Also include the new call
    updated_routes.insert(0, {
        "id": call.id,
        "type": call.type,
        "dst": call.dst,
        "severity": call.severity,
        "eta": cost,
        "path": path,
    })

    return {
        "call": {
            "id": call.id,
            "type": call.type,
            "dst": call.dst,
            "severity": call.severity,
            "path": path,
            "cost": cost,
            "eta": cost,
        },
        "queue": updated_routes,
    }


# ── GET /queue ────────────────────────────────────────────────────────────

@app.get("/queue", tags=["triage"])
def get_queue() -> dict:
    """Return the current triage queue with each call's ETA and path."""
    adj = _adj()

    from backend.app.graph.dijkstra import dijkstra as dijkstra_func

    queue_calls = triage_queue.get_all()
    result_calls = []

    for call in queue_calls:
        try:
            path, cost, _ = dijkstra_func(adj, "N01", call.dst)
            result_calls.append({
                "id": call.id,
                "type": call.type,
                "dst": call.dst,
                "severity": call.severity,
                "eta": cost,
                "path": path,
            })
        except Exception:
            result_calls.append({
                "id": call.id,
                "type": call.type,
                "dst": call.dst,
                "severity": call.severity,
                "eta": None,
                "path": None,
            })

    return {"queue": result_calls}


# ── POST /reset ───────────────────────────────────────────────────────────

@app.post("/reset", tags=["api"])
def reset_graph() -> dict:
    """Restore all edges to unblocked and clear active calls."""
    from backend.app.graph.seed import reset_db as reset_db_func
    reset_db_func()
    global active_calls
    active_calls = []
    # Also clear the triage queue
    triage_queue = type(triage_queue)()
    return {"reset": True, "message": "All edges unblocked, active calls cleared, queue cleared"}


# ── Development server ─────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)