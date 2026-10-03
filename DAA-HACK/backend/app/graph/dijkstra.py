"""Dijkstra's shortest path algorithm for CodeBlue Nav."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Set
import heapq


class NoPathError(Exception):
    """Raised when no path exists between src and dst given blocked edges.

    Accepts an optional message; call as NoPathError() or NoPathError(msg).
    """
    def __init__(self, msg=""):
        self.msg = msg
        super().__init__(msg)


@dataclass
class DijkstraStats:
    nodes_settled: int
    edges_relaxed: int


def dijkstra(
    adj: Dict[str, List[Tuple[str, float, str]]],
    src: str,
    dst: str,
    blocked_edges: Optional[Set[str]] = None,
) -> Tuple[List[str], float, DijkstraStats]:
    """
    Find the shortest path from src to dst using Dijkstra's algorithm.

    Args:
        adj: Adjacency dict {node_id: [(neighbor, weight, edge_label)]}
        src: Source node ID
        dst: Destination node ID
        blocked_edges: Set of edge IDs that are blocked/inaccessible

    Returns:
        (path, cost, stats) where path is a list of node IDs from src to dst,
        cost is total weight (seconds), and stats contains algorithm metrics.

    Raises:
        NoPathError: When dst is unreachable from src given blocked edges.
    """
    if blocked_edges is None:
        blocked_edges = set()

    if src == dst:
        return [src], 0.0, DijkstraStats(nodes_settled=0, edges_relaxed=0)

    # Priority queue: (cost_so_far, node, path_so_far)
    # We use a min-heap ordered by cost
    pq: List[Tuple[float, str, List[str]]] = [(0.0, src, [src])]
    visited: Set[str] = set()

    nodes_settled = 0
    edges_relaxed = 0

    while pq:
        cost_so_far, node, path = heapq.heappop(pq)
        nodes_settled += 1

        if node in visited:
            continue
        visited.add(node)

        if node == dst:
            return path, cost_so_far, DijkstraStats(
                nodes_settled=nodes_settled, edges_relaxed=edges_relaxed
            )

        for neighbor, weight, edge_label in adj.get(node, []):
            if edge_label in blocked_edges:
                continue  # Skip blocked edges
            if neighbor in visited:
                continue
            edges_relaxed += 1
            new_cost = cost_so_far + weight
            heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    raise NoPathError(f"No path from {src} to {dst} with blocked edges {blocked_edges}")