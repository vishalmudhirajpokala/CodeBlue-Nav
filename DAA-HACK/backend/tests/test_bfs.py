"""Pytest tests for BFS baseline algorithm."""

import pytest
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, PROJECT_ROOT)

# Import seed module directly
from seed_graph import reset_db, get_adjacency_list
from backend.app.graph.bfs import bfs
from backend.app.graph.dijkstra import NoPathError


# Reset database before tests
reset_db()


def get_adj():
    """Get fresh adjacency list."""
    return get_adjacency_list()


@pytest.fixture(autouse=True)
def reset_each_test():
    """Reset database before each test function."""
    reset_db()


class TestBFSShortestHops:
    """Test (a): BFS finds shortest path in terms of hops."""

    def test_bfs_n01_to_n10_fewest_hops(self):
        """BFS should find path with fewest hops from Central Station to OR Block."""
        adj = get_adj()
        result = bfs(adj, "N01", "N10")
        assert result.path == ["N01", "N02", "N11", "N10"]
        assert result.cost == 3.0  # 3 hops

    def test_bfs_n01_to_n12_fewest_hops(self):
        """BFS should find N01->N12 with fewest hops."""
        adj = get_adj()
        result = bfs(adj, "N01", "N12")
        assert result.path == ["N01", "N03", "N12"]
        assert result.cost == 2.0  # 2 hops

    def test_bfs_n01_to_n06_fewest_hops(self):
        """BFS should find N01->N06 with fewest hops."""
        adj = get_adj()
        result = bfs(adj, "N01", "N06")
        assert result.path == ["N01", "N03", "N05", "N06"]
        assert result.cost == 3.0  # 3 hops


class TestBFSWithBlockedEdges:
    """Test (b): BFS respects blocked edges."""

    def test_bfs_block_corridor_c(self):
        """BFS should respect blocked Corridor C edges."""
        adj = get_adj()
        adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14"})
        result = bfs(adj_blocked, "N01", "N06")
        assert result.path == ["N01", "N03", "N05", "N06"]
        assert result.cost == 3.0


class TestBFSNoPathError:
    """Test (c): BFS raises NoPathError when all paths blocked."""

    def test_bfs_no_path_when_all_routes_blocked(self):
        """Blocking E13, E14, and E21 should make N14 unreachable from N01."""
        adj = get_adj()
        adj_blocked = get_adjacency_list(blocked_edges={"E13", "E14", "E21"})
        with pytest.raises(NoPathError):
            bfs(adj_blocked, "N01", "N14")

    def test_bfs_src_equals_dst(self):
        """BFS should handle src == dst case."""
        adj = get_adj()
        result = bfs(adj, "N01", "N01")
        assert result.path == ["N01"]
        assert result.cost == 0.0