"""
Meterless World Model Package for AgriResolve.
Persistent, queryable, evolving graph of entities, contexts, and relationships.
Domain-agnostic, append-friendly, and idempotent per official specification.
"""

from .engine import WorldModel, WorldModelError
from .stable_id import (
    compute_content_checksum,
    compute_stable_context_id,
    compute_stable_entity_id,
    compute_stable_relationship_id,
)
from .store import CanonicalEventStore
from .types import (
    Context,
    Entity,
    Provenance,
    Relationship,
    WorldEvent,
    WorldEventType,
)
from .views import DisputeView, GraphView, TimelineView

__all__ = [
    "WorldModel",
    "WorldModelError",
    "CanonicalEventStore",
    "Entity",
    "Context",
    "Relationship",
    "Provenance",
    "WorldEvent",
    "WorldEventType",
    "GraphView",
    "TimelineView",
    "DisputeView",
    "compute_content_checksum",
    "compute_stable_entity_id",
    "compute_stable_context_id",
    "compute_stable_relationship_id",
]
