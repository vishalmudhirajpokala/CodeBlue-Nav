"""Breadth-First Search (BFS) baseline for unweighted hop-count.

BFS finds the path with the fewest hops (edges) regardless of weight.
Used as a comparison baseline against Dijkstra (shortest total weight).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Set, Dict

from .dijkstra import NoPathError, DijkstraStats


@dataclass
class BFSResult:
    path: List[str]
    cost: float  # Number of hops (len(path) - 1)
    stats: DijkstraStats


def bfs(
    adj: Dict[str, List[Tuple[str, float, str]]],
    src: str,
    dst: str,
    blocked_edges: Optional[Set[str]] = None,
) -> BFSResult:
    """
    Find the shortest path (fewest hops) from src to dst using BFS.

    Args:
        adj: Adjacency dict {node_id: [(neighbor, weight, edge_label)]}
        src: Source node ID
        dst: Destination node ID
        blocked_edges: Set of edge IDs that are blocked/inaccessible

    Returns:
        BFSResult containing path, cost (in hops), and stats.

    Raises:
        NoPathError: When dst is unreachable from src given blocked edges.
    """
    if blocked_edges is None:
        blocked_edges = set()

    if src == dst:
        return BFSResult(path=[src], cost=0.0, stats=DijkstraStats(nodes_settled=0, edges_relaxed=0))

    # Standard BFS using a queue
    # Queue entries: (current_node, path_so_far)
    queue: List[Tuple[str, List[str]]] = [(src, [src])]
    visited: Set[str] = {src}

    nodes_visited = 0

    while queue:
        node, path = queue.pop(0)  # FIFO queue
        nodes_visited += 1

        for neighbor, weight, edge_label in adj.get(node, []):
            if edge_label in blocked_edges:
                continue  # Skip blocked edges
            if neighbor in visited:
                continue

            new_path = path + [neighbor]

            if neighbor == dst:
                cost = len(new_path) - 1  # number of hops
                stats = DijkstraStats(
                    nodes_settled=nodes_visited,
                    edges_relaxed=nodes_visited,
                )
                return BFSResult(path=new_path, cost=float(cost), stats=stats)

            visited.add(neighbor)
            queue.append((neighbor, new_path))

    raise NoPathError(f"No path from {src} to {dst} with blocked edges {blocked_edges}")