"""Test the FastAPI endpoints using httpx."""

import sys
import time
import os

sys.path.insert(0, r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

from backend.app.graph.seed import reset_db, get_adjacency_list
from backend.app.graph.dijkstra import dijkstra, NoPathError
from backend.app.graph.bfs import bf

# First, reset and verify the graph works
reset_db()
adj = get_adjacency_list()

# Test Dijkstra and BFS first
path, cost, stats = dijkstra(adj, "N01", "N10")
print(f"Dijkstra N01->N10: path={path}, cost={cost}")

# Now test the API using httpx
try:
    import httpx
    print("httpx available, testing API...")
except ImportError:
    print("httpx not available, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

base = "http://127.0.0.1:8000"

# Reset database first
print("Resetting database...")
r = f"{base}/reset"
resp = requests = __import__('requests') if True else httpx
# Use httpx instead
import httpx
cli = httpx.Client(base_url=base, timeout=10.0)

print("Testing GET /graph...")
r = cli.get("/graph")
print(f"  Status: {r.status_code}")
print(f"  Nodes: {len(r.json().get('nodes', []))}")
print(f"  Edges: {len(r.json().get('edges', []))}")

print("Testing POST /route...")
r = cli.post("/route", json={"src": "N01", "dst": "N10", "algo": "dijkstra"})
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {data}")
assert data["path"] == ["N01", "N02", "N11", "N10"]
assert data["cost"] == 140.0

print("Testing POST /simulate/block...")
r = cli.post("/simulate/block", json={"edge_id": "E13"})
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {data}")

print("Testing POST /route after blocking...")
r = cli.post("/route", json={"src": "N01", "dst": "N06", "algo": "dijkstra"})
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {data}")

print("Testing GET /reset...")
r = cli.get("/reset")
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {data}")

cli.close()
print("\nAll API tests passed!")