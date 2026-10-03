"""Test the FastAPI endpoints using httpx."""

import httpx
import time
import sys
import subprocess

# Make sure the server is running
sys.path.insert(0, r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

base = "http://127.0.0.1:8000"
cli = httpx.Client(base_url=base, timeout=10.0)

print("=== GET /graph ===")
r = cli.get("/graph")
print(f"Status: {r.status_code}")
data = r.json()
print(f"Nodes: {len(data['nodes'])}")
print(f"Edges: {len(data['edges'])}")

print("\n=== POST /route (dijkstra N01->N10) ===")
r = cli.post("/route", json={"src": "N01", "dst": "N10", "algo": "dijkstra"})
print(f"Status: {r.status_code}")
data = r.json()
print(f"Path: {data['path']}")
print(f"Cost: {data['cost']}")

print("\n=== POST /simulate/block E13 ===")
r = cli.post("/simulate/block", json={"edge_id": "E13"})
print(f"Status: {r.status_code}")
data = r.json()
print(f"Edge blocked: {data['edge_blocked']}")

print("\n=== POST /route (dijkstra N01->N06, C blocked) ===")
r = cli.post("/route", json={"src": "N01", "dst": "N06", "algo": "dijkstra"})
print(f"Status: {r.status_code}")
data = r.json()
print(f"Path: {data['path']}")
print(f"Cost: {data['cost']}")

print("\n=== GET /reset ===")
r = cli.get("/reset")
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {data}")

cli.close()
print("\nAll API tests completed!")