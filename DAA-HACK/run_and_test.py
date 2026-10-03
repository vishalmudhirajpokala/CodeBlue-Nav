#!/usr/bin/env python3
"""Start the FastAPI server and test all endpoints."""

import subprocess
import sys
import time
import os

sys.path.insert(0, r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

# Start the server
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.app.main:app",
     "--host", "127.0.0.1", "--port", "8000", "--reload"],
    cwd=r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for server to start
time.sleep(3)

try:
    import httpx
    cli = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

    print("=" * 50)
    print("TEST 1: GET /graph")
    print("=" * 50)
    r = cli.get("/graph")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Nodes: {len(data['nodes'])}")
    print(f"Edges: {len(data['edges'])}")

    print("\n" + "=" * 50)
    print("TEST 2: POST /route (dijkstra N01->N10)")
    print("=" * 50)
    r = cli.post("/route", json={"src": "N01", "dst": "N10", "algo": "dijkstra"})
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Path: {data['path']}")
    print(f"Cost: {data['cost']}s")
    assert data["path"] == ["N01", "N02", "N11", "N10"], f"Expected shortest path, got {data['path']}"
    assert data["cost"] == 140.0, f"Expected cost 140, got {data['cost']}"
    print("PASSED")

    print("\n" + "=" * 50)
    print("TEST 3: POST /simulate/block E13 (Corridor C)")
    print("=" * 50)
    r = cli.post("/simulate/block", json={"edge_id": "E13"})
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Edge blocked: {data['edge_blocked']}")
    assert data["edge_blocked"] is True

    print("\n" + "=" * 50)
    print("TEST 4: POST /route (dijkstra N01->N06, C blocked)")
    print("=" * 50)
    r = cli.post("/route", json={"src": "N01", "dst": "N06", "algo": "dijkstra"})
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Path: {data['path']}")
    print(f"Cost: {data['cost']}s")
    # After blocking Corridor C, should take detour
    assert data["cost"] == 130.0, f"Expected 130 with detour, got {data['cost']}"
    print("PASSED")

    print("\n" + "=" * 50)
    print("TEST 5: GET /reset")
    print("=" * 50)
    r = cli.get("/reset")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Response: {data}")
    assert data["reset"] is True

    cli.close()
    print("\n" + "=" * 50)
    print("ALL API TESTS PASSED!")
    print("=" * 50)

finally:
    # Stop the server
    proc.terminate()
    proc.wait(timeout=5)
    print("\nServer stopped.")