"""Triage models for CodeBlue Nav."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Call:
    """Represents a triage call with routing information."""
    id: str
    type: str
    severity: int
    dst: str
    status: str = "active"
    path: list | None = None  # Route from N01 to dst
    cost: float = 0.0  # Total seconds
    eta: float = 0.0  # Estimated time in seconds


@dataclass
class QueueSnapshot:
    """A snapshot of the current triage queue state."""
    calls: list[Call]
    graph_state: dict  # node/edge blockage info
    route_stats: dict  # total calls, avg ETA, etc.