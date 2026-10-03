"""Verify NoPathError is raised when all paths blocked."""

import sys
sys.path.insert(0, r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

import seed_graph
seed_graph.reset_db()

from seed_graph import get_adjacency_list
from backend.app.graph.dijkstra import dijkstra, NoPathError

adj = get_adjacency_list()

# Block ALL edges connecting to N14: E13, E14, E21
adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14", "E21"})

print("Blocked E13, E14, E21:")
for n in sorted(adj_blocked.keys()):
    nb = adj_blocked[n]
    print(f"  {n} -> {nb}")

print("\nTrying dijkstra N01 -> N14 with E13, E14, E21 blocked:")
try:
    path, cost, stats = dijkstra(adj_blocked, "N01", "N14")
    print(f"  UNEXPECTED: path = {path}, cost = {cost}")
except NoPathError as e:
    print(f"  Correctly raised NoPathError: {e}")