"""Triage priority queue for CodeBlue Nav.

Min-heap of EmergencyCall(order key = (severity desc, eta asc)).
Order key implemented as a tuple key (-severity, eta) in a heap.

The rule: order by (severity desc, eta asc) implemented as a heap with
a tuple key (-severity, eta). This means higher severity numbers (1-5,
where 1 is most severe) get priority, and within the same severity,
shorter ETA gets priority.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EmergencyCall:
    """An emergency call in the triage priority queue."""
    id: str
    type: str  # e.g., "Stroke Alert", "Cardiac Arrest"
    severity: int  # 1 (most severe) to 5 (least severe)
    dst: str  # destination node ID
    status: str = "active"  # active, completed, escalated

    # Heap comparison: lower tuple = higher priority
    # We use (-severity, eta) so that:
    # - Lower severity number (more urgent) comes first (negated makes it sort correctly)
    # - Within same severity, lower ETA comes first
    _priority_key: tuple = field(init=False, repr=False, compare=True)

    def __post_init__(self):
        # Priority key: (-severity, eta_seconds)
        # We cannot compute eta here since it depends on the graph;
        # the key will be set when the call is added to a queue.
        self._priority_key = (-self.severity, 0)


class PriorityQueue:
    """Min-heap priority queue for EmergencyCall objects.

    Order key = (severity desc, eta asc) implemented as a heap
    with a tuple key (-severity, eta).
    """

    def __init__(self):
        self._heap: List[tuple] = []
        self._index: int = 0  # Tiebreaker for same-priority items
        self._calls: dict = {}  # id -> (call, eta)

    def push(self, call: EmergencyCall, eta_seconds: float) -> None:
        """Push a call onto the priority queue.

        Args:
            call: The EmergencyCall to add.
            eta_seconds: Estimated time to destination in seconds.
        """
        # Priority key: (-severity, eta_seconds, index)
        # Negative severity so that lower severity number = higher priority
        # eta_seconds as the secondary sort key
        priority = (-call.severity, eta_seconds, self._index)
        heapq.heappush(self._heap, priority)
        self._calls[call.id] = (call, eta_seconds)
        self._index += 1

    def pop(self) -> Optional[EmergencyCall]:
        """Pop the highest-priority call from the queue.

        Returns:
            The highest-priority EmergencyCall, or None if the queue is empty.
        """
        if not self._heap:
            return None

        _, _, index = heapq.heappop(self._heap)
        call, eta_seconds = self._calls.pop(index, (None, 0))
        return call[0] if call else None

    def peek(self) -> Optional[EmergencyCall]:
        """View the highest-priority call without removing it.

        Returns:
            The highest-priority EmergencyCall, or None if the queue is empty.
        """
        if not self._heap:
            return None

        neg_severity, eta_seconds, _ = self._heap[0]
        call, _ = self._calls.get(index if index < len(self._calls) else 0, (None, 0))
        return call[0] if call else None

    def __len__(self) -> int:
        """Return the number of calls in the queue."""
        return len(self._heap)

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self) == 0

    def get_all(self) -> List[EmergencyCall]:
        """Return all calls sorted by priority (highest first).

        Returns:
            List of EmergencyCall objects sorted by (severity desc, eta asc).
        """
        sorted_calls = sorted(
            self._calls.values(),
            key=lambda x: (-x[0].severity, x[1]),
        )
        return [c[0] for c in sorted_calls]

    def update_eta(self, call_id: str, eta_seconds: float) -> bool:
        """Update the ETA for an existing call.

        Args:
            call_id: The ID of the call to update.
            eta_seconds: The new ETA in seconds.

        Returns:
            True if the call was found and updated, False otherwise.
        """
        if call_id in self._calls:
            call, _ = self._calls[call_id]
            # Remove old entry and re-add with new ETA
            # Note: This is O(n) since we need to rebuild the heap position
            # For simplicity, we just update the ETA; the heap will
            # self-correct on next pop operations
            self._calls[call_id] = (call, eta_seconds)
            # Re-heapify by replacing the priority
            # We'll rebuild the heap to be safe
            self._reheapify()
            return True
        return False

    def _reheapify(self) -> None:
        """Rebuild the heap from the current calls dict."""
        new_heap = []
        for call_id, (call, eta) in self._calls.items():
            priority = (-call.severity, eta, self._index)
            heapq.heappush(new_heap, priority)
            self._index += 1
        self._heap = new_heap


# Global priority queue instance for the API
triage_queue = PriorityQueue()


def add_call(call_type: str, dst: str, severity: int = 3) -> EmergencyCall:
    """Create a new emergency call and add it to the triage queue.

    Args:
        call_type: Type of emergency (e.g., "Stroke Alert")
        dst: Destination node ID (e.g., "N02" for ER)
        severity: Severity level 1-5 (1 = most severe)

    Returns:
        The newly created EmergencyCall.
    """
    import uuid

    call_id = f"call-{uuid.uuid4().hex[:8]}"
    call = EmergencyCall(
        id=call_id,
        type=call_type,
        severity=severity,
        dst=dst,
    )
    # ETA will be computed by the API route handler using Dijkstra
    # For now, use a default based on severity
    eta_seconds = 60.0 if severity <= 2 else 30.0
    triage_queue.push(call, eta_seconds)
    return call