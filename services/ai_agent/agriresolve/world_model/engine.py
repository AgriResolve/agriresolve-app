"""
Meterless World Model Engine for AgriResolve.
Coordinates the ingest pipeline, canonical event store, and derived views.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .stable_id import (
    compute_content_checksum,
    compute_stable_context_id,
    compute_stable_entity_id,
    compute_stable_relationship_id,
)
from .store import CanonicalEventStore
from .types import Context, Entity, Provenance, Relationship, WorldEvent, WorldEventType
from .views import DisputeView, GraphView, TimelineView


class WorldModelError(Exception):
    """Raised when world model invariants or validations are violated."""
    pass


class WorldModel:
    """
    Meterless World Model engine instance.
    Persistent, queryable, evolving graph of entities, contexts, and relationships.
    """

    def __init__(self, store: Optional[CanonicalEventStore] = None):
        self.store = store or CanonicalEventStore()

        # Initialize derived views
        self.graph_view = GraphView()
        self.timeline_view = TimelineView()
        self.dispute_view = DisputeView()

        # Register view reducers with the store
        self.store.subscribe(self._on_event_appended)

    def _on_event_appended(self, event: WorldEvent) -> None:
        self.graph_view.apply_event(event)
        self.timeline_view.apply_event(event)
        self.dispute_view.apply_event(event)

    def rebuild_views(self) -> None:
        """
        Wipes all derived views and replays the canonical event store from the beginning.
        Demonstrates that views are strictly derived and rebuildable from the store.
        """
        self.graph_view.reset()
        self.timeline_view.reset()
        self.dispute_view.reset()

        for event in self.store.replay_events():
            self._on_event_appended(event)

    def view(self, name: str) -> Any:
        """
        Accessor for derived views: 'graph', 'timeline', 'dispute'.
        """
        v = name.strip().lower()
        if v == "graph":
            return self.graph_view
        elif v == "timeline":
            return self.timeline_view
        elif v in ("dispute", "disputes"):
            return self.dispute_view
        else:
            raise WorldModelError(f"Unknown view: '{name}'. Available views: 'graph', 'timeline', 'dispute'.")

    # =========================================================================
    # Pipeline Ingestion Interface (Idempotent & Provenance-Enforced)
    # =========================================================================

    def upsert_context(
        self,
        context_type: str,
        canonical_key: str,
        attrs: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        """
        Ingests a bounded context with a deterministic stable ID.
        """
        attrs = attrs or {}
        context_id = compute_stable_context_id(context_type, canonical_key, parent_id)
        now_ts = datetime.now(timezone.utc).isoformat()

        # Deterministic dedupe key for event
        event_id = f"evt_ctx_{context_id}"
        event = WorldEvent(
            event_id=event_id,
            event_type=WorldEventType.UPSERT_CONTEXT,
            timestamp=now_ts,
            context_id=context_id,
            payload={
                "id": context_id,
                "type": context_type,
                "attrs": attrs,
                "parent_id": parent_id,
            },
        )
        self.store.append_event(event)
        return context_id

    def upsert_entity(
        self,
        entity_type: str,
        canonical_key: str,
        attrs: Dict[str, Any],
        provenance: Provenance,
        context_id: Optional[str] = None,
    ) -> str:
        """
        Ingests an entity with mandatory provenance and deterministic stable ID.
        """
        if not provenance:
            raise WorldModelError("Provenance is mandatory for every entity record.")

        entity_id = compute_stable_entity_id(entity_type, canonical_key)
        now_ts = datetime.now(timezone.utc).isoformat()

        # Compute checksum if not provided
        if not provenance.checksum:
            checksum = compute_content_checksum(attrs)
            provenance = Provenance(
                source_id=provenance.source_id,
                source_type=provenance.source_type,
                recorded_at=provenance.recorded_at,
                checksum=checksum,
                metadata=provenance.metadata,
            )

        # Event deduplication key based on entity_id and content checksum
        event_id = f"evt_ent_{entity_id}_{provenance.checksum[:8]}"
        event = WorldEvent(
            event_id=event_id,
            event_type=WorldEventType.UPSERT_ENTITY,
            timestamp=now_ts,
            context_id=context_id or "global",
            payload={
                "id": entity_id,
                "type": entity_type,
                "attrs": attrs,
                "provenance": provenance.to_dict(),
            },
            provenance=provenance,
        )
        self.store.append_event(event)
        return entity_id

    def relate(
        self,
        from_id: str,
        rel_type: str,
        to_id: str,
        context_id: Optional[str] = None,
        attrs: Optional[Dict[str, Any]] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        provenance: Optional[Provenance] = None,
    ) -> str:
        """
        Creates or updates a typed relationship with a deterministic stable ID.
        """
        attrs = attrs or {}
        rel_id = compute_stable_relationship_id(from_id, rel_type, to_id, context_id)
        now_ts = datetime.now(timezone.utc).isoformat()

        event_id = f"evt_{rel_id}"
        event = WorldEvent(
            event_id=event_id,
            event_type=WorldEventType.RELATE,
            timestamp=now_ts,
            context_id=context_id or "global",
            payload={
                "id": rel_id,
                "from_id": from_id,
                "type": rel_type,
                "to_id": to_id,
                "context_id": context_id,
                "attrs": attrs,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "provenance": provenance.to_dict() if provenance else None,
            },
            provenance=provenance,
        )
        self.store.append_event(event)
        return rel_id

    def record_observation(
        self,
        context_id: str,
        observation_name: str,
        data: Dict[str, Any],
        provenance: Optional[Provenance] = None,
    ) -> str:
        """
        Appends an empirical observation to the context log.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        checksum = compute_content_checksum(data)
        event_id = f"evt_obs_{context_id}_{observation_name}_{checksum[:8]}"

        event = WorldEvent(
            event_id=event_id,
            event_type=WorldEventType.RECORD_OBSERVATION,
            timestamp=now_ts,
            context_id=context_id,
            payload={
                "observation_name": observation_name,
                "data": data,
                "checksum": checksum,
            },
            provenance=provenance,
        )
        self.store.append_event(event)
        return event_id

    def transition_state(
        self,
        context_id: str,
        from_state: str,
        to_state: str,
        reason: str,
        provenance: Optional[Provenance] = None,
    ) -> str:
        """
        Appends an explicit investigation state change to the event log.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        event_id = f"evt_state_{context_id}_{to_state}_{uuid.uuid4().hex[:6]}"

        event = WorldEvent(
            event_id=event_id,
            event_type=WorldEventType.TRANSITION_STATE,
            timestamp=now_ts,
            context_id=context_id,
            payload={
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
            },
            provenance=provenance,
        )
        self.store.append_event(event)
        return event_id
