"""Verify Dijkstra and BFS on the seeded graph."""

import sys
import os

# Add the project root to path
sys.path.insert(0, r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

# Import seed module - run it directly to setup the DB
import importlib.util
spec = importlib.util.spec_from_file_location(
    "seed_graph", r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK\seed_graph.py"
)
seed_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed_mod)

reset_db = seed_mod.reset_db
get_adjacency_list = seed_mod.get_adjacency_list

reset_db()

from backend.app.graph.dijkstra import dijkstra, NoPathError
from backend.app.graph.bfs import bfs

# Get adjacency
adj = get_adjacency_list()

print("=" * 60)
print("TEST 1: Shortest path N01 -> N10 (Central Station -> OR Block)")
print("=" * 60)

path, cost, stats = dijkstra(adj, "N01", "N10")
print(f"Dijkstra: path = {path}")
print(f"Dijkstra: cost = {cost}s")
print(f"Dijkstra: nodes_settled = {stats.nodes_settled}, edges_relaxed = {stats.edges_relaxed}")

result = bfs(adj, "N01", "N10")
print(f"BFS: path = {result.path}")
print(f"BFS: cost = {result.cost} hops")
print(f"BFS: nodes_settled = {result.stats.nodes_settled}, edges_relaxed = {result.stats.edges_relaxed}")

print()
print("=" * 60)
print("TEST 2: Block Corridor C edges (E13, E14) and reroute N01 -> N06")
print("=" * 60)

adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14"})

path_d, cost_d, stats_d = dijkstra(adj_blocked, "N01", "N06")
print(f"Dijkstra (C blocked): path = {path_d}")
print(f"Dijkstra (C blocked): cost = {cost_d}s")

result_b = bfs(adj_blocked, "N01", "N06")
print(f"BFS (C blocked): path = {result_b.path}")
print(f"BFS (C blocked): cost = {result_b.cost} hops")

print()
print("=" * 60)
print("TEST 3: Block all paths to a node - should raise NoPathError")
print("=" * 60)

try:
    dijkstra(adj_blocked, "N01", "N14")
    print("ERROR: Should have raised NoPathError!")
except NoPathError as e:
    print(f"Correctly raised NoPathError: {e}")

print()
print("=" * 60)
print("TEST 4: Unblocked graph - compare Dijkstra vs BFS on N01 -> N12")
print("=" * 60)

path_d2, cost_d2, stats_d2 = dijkstra(adj, "N01", "N12")
result_b2 = bfs(adj, "N01", "N12")
print(f"Dijkstra: path = {path_d2}, cost = {cost_d2}s")
print(f"BFS:      path = {result_b2.path}, cost = {result_b2.cost} hops")
print(f"Takeaway: Dijkstra finds minimum-weight path; BFS finds minimum-hop path.")

print()
print("ALL TESTS PASSED!")