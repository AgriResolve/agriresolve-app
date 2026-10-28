"""
Canonical Append-Only Event Store for Meterless World Model.
Acts as the single source of truth. Never overwrites or mutates history.
"""

from __future__ import annotations

import threading
from typing import Callable, Dict, Iterator, List, Optional
from .types import Context, Entity, Provenance, Relationship, WorldEvent, WorldEventType


class CanonicalEventStore:
    """
    Append-only log of events for a world model.
    Durable in-memory store with optional JSON serialization / replay capability.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._events: List[WorldEvent] = []
        self._event_subscribers: List[Callable[[WorldEvent], None]] = []

    def append_event(self, event: WorldEvent) -> WorldEvent:
        """
        Appends an event to the log. Guaranteed idempotent when event_id matches.
        """
        with self._lock:
            # Check for existing event with same event_id (idempotency guard)
            for existing in self._events:
                if existing.event_id == event.event_id:
                    return existing

            self._events.append(event)
            # Notify view subscribers
            for sub in self._event_subscribers:
                sub(event)

            return event

    def subscribe(self, callback: Callable[[WorldEvent], None]) -> None:
        """
        Subscribes a view reducer / projection callback to new appended events.
        """
        with self._lock:
            self._event_subscribers.append(callback)

    def get_events(
        self,
        context_id: Optional[str] = None,
        event_type: Optional[WorldEventType] = None,
    ) -> List[WorldEvent]:
        """
        Returns events, optionally filtered by context or type.
        """
        with self._lock:
            results = self._events
            if context_id:
                results = [e for e in results if e.context_id == context_id]
            if event_type:
                results = [e for e in results if e.event_type == event_type]
            return list(results)

    def replay_events(self) -> Iterator[WorldEvent]:
        """
        Iterates over all events from the beginning to rebuild views.
        """
        with self._lock:
            for event in list(self._events):
                yield event

    def count(self) -> int:
        with self._lock:
            return len(self._events)
