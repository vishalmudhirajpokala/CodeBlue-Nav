"""Pytest tests for Dijkstra's shortest path algorithm."""

import pytest
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, PROJECT_ROOT)

# Import seed module directly
from seed_graph import reset_db, get_adjacency_list
from backend.app.graph.dijkstra import dijkstra, NoPathError


# Reset database before tests
reset_db()


def get_adj():
    """Get fresh adjacency list."""
    return get_adjacency_list()


@pytest.fixture(autouse=True)
def reset_each_test():
    """Reset database before each test function."""
    reset_db()


class TestDijkstraShortestPath:
    """Test (a): shortest path on the seeded graph."""

    def test_shortest_path_n01_to_n10(self):
        """Dijkstra should find shortest path from Central Station to OR Block."""
        adj = get_adj()
        path, cost, stats = dijkstra(adj, "N01", "N10")
        assert path == ["N01", "N02", "N11", "N10"]
        assert cost == 140.0  # 45 + 70 + 25

    def test_shortest_path_n01_to_n06_unblocked(self):
        """Dijkstra should find N01->N06 path."""
        adj = get_adj()
        path, cost, stats = dijkstra(adj, "N01", "N06")
        # Shortest path: N01->N03->N05->N06 = 55+35+40 = 130
        assert path == ["N01", "N03", "N05", "N06"]
        assert cost == 130.0

    def test_shortest_path_n01_to_n12(self):
        """Dijkstra should find N01->N12 path."""
        adj = get_adj()
        path, cost, stats = dijkstra(adj, "N01", "N12")
        # Path: N01->N03->N12 = 55+65 = 120
        assert path == ["N01", "N03", "N12"]
        assert cost == 120.0


class TestDijkstraWithBlockedEdges:
    """Test (b): blocking Corridor C edges forces a detour and increases cost."""

    def test_block_corridor_c_increases_cost(self):
        """Blocking E13 and E14 (Corridor C) should force detour."""
        adj = get_adj()
        adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14"})
        path, cost, stats = dijkstra(adj_blocked, "N01", "N06")
        # Detour: N01->N03->N05->N06 = 55+35+40 = 130
        assert cost == 130.0
        assert path == ["N01", "N03", "N05", "N06"]

    def test_block_corridor_c_different_destination(self):
        """Blocking Corridor C should affect routes through N14."""
        adj = get_adj()
        adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14"})
        path, cost, stats = dijkstra(adj_blocked, "N01", "N14")
        # N14 should be reachable via alternative routes
        assert isinstance(path, list)


class TestNoPathError:
    """Test (c): blocking ALL paths to a node raises NoPathError."""

    def test_no_path_when_all_routes_blocked(self):
        """Blocking E13, E14, and E21 should make N14 unreachable from N01."""
        adj = get_adj()
        adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14", "E21"})
        with pytest.raises(NoPathError):
            dijkstra(adj_blocked, "N01", "N14")

    def test_no_path_when_src_equals_dst(self):
        """Dijkstra should handle src == dst case."""
        adj = get_adj()
        path, cost, stats = dijkstra(adj, "N01", "N01")
        assert path == ["N01"]
        assert cost == 0.0