"""
Core data model types for Meterless World Model specification.
Defines Entities, Contexts, Relationships, Provenance, and Append-Only Events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Provenance:
    """
    Mandatory audit block for every entity, relationship, and observation.
    """
    source_id: str
    source_type: str
    recorded_at: str
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "recorded_at": self.recorded_at,
            "checksum": self.checksum,
            "metadata": dict(self.metadata),
        }


@dataclass
class Entity:
    """
    Discrete, identifiable thing with a stable content-addressed ID.
    """
    id: str
    type: str
    attrs: Dict[str, Any]
    provenance: Provenance
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "attrs": self.attrs,
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at,
            "version": self.version,
        }


@dataclass
class Context:
    """
    A bounded situation in which facts and relationships hold (e.g. a dispute, a session).
    """
    id: str
    type: str
    attrs: Dict[str, Any]
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "attrs": self.attrs,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
        }


@dataclass
class Relationship:
    """
    Typed edge connecting two entities, scoped to a context, with provenance.
    """
    id: str
    from_id: str
    type: str
    to_id: str
    context_id: Optional[str] = None
    attrs: Dict[str, Any] = field(default_factory=dict)
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    provenance: Optional[Provenance] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_id": self.from_id,
            "type": self.type,
            "to_id": self.to_id,
            "context_id": self.context_id,
            "attrs": self.attrs,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }


class WorldEventType(str, Enum):
    UPSERT_CONTEXT = "upsert_context"
    UPSERT_ENTITY = "upsert_entity"
    RELATE = "relate"
    RECORD_OBSERVATION = "record_observation"
    TRANSITION_STATE = "transition_state"


@dataclass
class WorldEvent:
    """
    Append-only event in the canonical event log.
    """
    event_id: str
    event_type: WorldEventType
    timestamp: str
    context_id: str
    payload: Dict[str, Any]
    provenance: Optional[Provenance] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "context_id": self.context_id,
            "payload": self.payload,
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }
