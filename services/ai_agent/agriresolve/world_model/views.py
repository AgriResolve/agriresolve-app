"""
Derived Views for Meterless World Model Read Surface.
Every view is a rebuildable projection folded over the canonical event store.
Never mutated independently of the event log.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from .types import Context, Entity, Provenance, Relationship, WorldEvent, WorldEventType


class GraphView:
    """
    Relational and traversal projection.
    Maintains entities, contexts, and typed relationships as an adjacency graph.
    """

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.contexts: Dict[str, Context] = {}
        self.relationships: Dict[str, Relationship] = {}
        self._out_edges: Dict[str, List[Relationship]] = {}
        self._in_edges: Dict[str, List[Relationship]] = {}

    def reset(self) -> None:
        self.entities.clear()
        self.contexts.clear()
        self.relationships.clear()
        self._out_edges.clear()
        self._in_edges.clear()

    def apply_event(self, event: WorldEvent) -> None:
        if event.event_type == WorldEventType.UPSERT_CONTEXT:
            ctx = Context(
                id=event.payload["id"],
                type=event.payload["type"],
                attrs=event.payload.get("attrs", {}),
                parent_id=event.payload.get("parent_id"),
                created_at=event.timestamp,
            )
            self.contexts[ctx.id] = ctx

        elif event.event_type == WorldEventType.UPSERT_ENTITY:
            prov_dict = event.payload.get("provenance", {})
            prov = Provenance(
                source_id=prov_dict.get("source_id", "UNKNOWN"),
                source_type=prov_dict.get("source_type", "observation"),
                recorded_at=prov_dict.get("recorded_at", event.timestamp),
                checksum=prov_dict.get("checksum", ""),
                metadata=prov_dict.get("metadata", {}),
            )
            ent_id = event.payload["id"]
            existing = self.entities.get(ent_id)
            version = (existing.version + 1) if existing else 1
            ent = Entity(
                id=ent_id,
                type=event.payload["type"],
                attrs=event.payload.get("attrs", {}),
                provenance=prov,
                created_at=event.timestamp,
                version=version,
            )
            self.entities[ent.id] = ent

        elif event.event_type == WorldEventType.RELATE:
            prov = None
            if event.payload.get("provenance"):
                pd = event.payload["provenance"]
                prov = Provenance(
                    source_id=pd.get("source_id", "relate"),
                    source_type=pd.get("source_type", "relate"),
                    recorded_at=pd.get("recorded_at", event.timestamp),
                    checksum=pd.get("checksum", ""),
                    metadata=pd.get("metadata", {}),
                )
            rel = Relationship(
                id=event.payload["id"],
                from_id=event.payload["from_id"],
                type=event.payload["type"],
                to_id=event.payload["to_id"],
                context_id=event.payload.get("context_id"),
                attrs=event.payload.get("attrs", {}),
                valid_from=event.payload.get("valid_from"),
                valid_to=event.payload.get("valid_to"),
                provenance=prov,
            )
            self.relationships[rel.id] = rel
            self._out_edges.setdefault(rel.from_id, []).append(rel)
            self._in_edges.setdefault(rel.to_id, []).append(rel)

    def neighbors_of(
        self,
        entity_id: str,
        via: Optional[str] = None,
        in_context: Optional[str] = None,
        direction: str = "out",
    ) -> List[Relationship]:
        """
        Finds connected relationships matching the filter.
        direction can be: 'out', 'in', or 'both'.
        """
        candidates: List[Relationship] = []
        if direction in ("out", "both"):
            candidates.extend(self._out_edges.get(entity_id, []))
        if direction in ("in", "both"):
            candidates.extend(self._in_edges.get(entity_id, []))

        results = []
        for rel in candidates:
            if via and rel.type != via:
                continue
            if in_context and rel.context_id != in_context:
                continue
            results.append(rel)
        return results

    def trace_provenance(self, finding_id: str) -> List[Entity]:
        """
        Recursively traverses 'derived_from' and 'supported_by' relationships
        to identify the root evidence documents that produced this finding.
        """
        visited: Set[str] = set()
        source_docs: List[Entity] = []

        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)

            # Check outgoing relationships where finding -> derived_from -> document
            for rel in self.neighbors_of(current_id, direction="out"):
                if rel.type in ("derived_from", "supported_by", "cites"):
                    target_ent = self.entities.get(rel.to_id)
                    if target_ent:
                        if target_ent.type == "evidence_document" and target_ent not in source_docs:
                            source_docs.append(target_ent)
                        traverse(target_ent.id)

            # Check incoming relationships where document -> supports -> finding
            for rel in self.neighbors_of(current_id, direction="in"):
                if rel.type in ("supports", "proves", "attests"):
                    source_ent = self.entities.get(rel.from_id)
                    if source_ent:
                        if source_ent.type == "evidence_document" and source_ent not in source_docs:
                            source_docs.append(source_ent)
                        traverse(source_ent.id)

        traverse(finding_id)
        return source_docs


class TimelineView:
    """
    Time-bounded query surface for chronological progression of events and observations.
    """

    def __init__(self):
        self.events: List[WorldEvent] = []

    def reset(self) -> None:
        self.events.clear()

    def apply_event(self, event: WorldEvent) -> None:
        self.events.append(event)

    def get_state_history(self, context_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns chronological history of investigation state transitions.
        """
        transitions = []
        for e in self.events:
            if e.event_type == WorldEventType.TRANSITION_STATE:
                if not context_id or e.context_id == context_id:
                    transitions.append({
                        "timestamp": e.timestamp,
                        "context_id": e.context_id,
                        "from_state": e.payload.get("from_state"),
                        "to_state": e.payload.get("to_state"),
                        "reason": e.payload.get("reason"),
                    })
        return transitions

    def get_observations(self, context_id: Optional[str] = None) -> List[WorldEvent]:
        obs = [e for e in self.events if e.event_type == WorldEventType.RECORD_OBSERVATION]
        if context_id:
            obs = [e for e in obs if e.context_id == context_id]
        return obs


class DisputeView:
    """
    Materialized state view of an active agricultural dispute.
    Reconstructed purely from the append-only event store.
    """

    def __init__(self):
        self.dispute_id: str = ""
        self.current_state: str = "uninitialized"
        self.parties: Dict[str, Dict[str, Any]] = {}
        self.claims: Dict[str, Dict[str, Any]] = {}
        self.evidence_documents: Dict[str, Dict[str, Any]] = {}
        self.contradictions: Dict[str, Dict[str, Any]] = {}
        self.findings: Dict[str, Dict[str, Any]] = {}
        self.evidence_requests: Dict[str, Dict[str, Any]] = {}
        self.evidence_log: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.dispute_id = ""
        self.current_state = "uninitialized"
        self.parties.clear()
        self.claims.clear()
        self.evidence_documents.clear()
        self.contradictions.clear()
        self.findings.clear()
        self.evidence_requests.clear()
        self.evidence_log.clear()

    def apply_event(self, event: WorldEvent) -> None:
        if event.event_type == WorldEventType.UPSERT_CONTEXT:
            self.dispute_id = event.payload.get("attrs", {}).get("dispute_id", event.payload["id"])

        elif event.event_type == WorldEventType.TRANSITION_STATE:
            self.current_state = event.payload.get("to_state", self.current_state)

        elif event.event_type == WorldEventType.UPSERT_ENTITY:
            ent_type = event.payload["type"]
            ent_id = event.payload["id"]
            attrs = event.payload.get("attrs", {})

            if ent_type == "party":
                self.parties[ent_id] = attrs
            elif ent_type == "claim":
                self.claims[ent_id] = attrs
            elif ent_type == "evidence_document":
                self.evidence_documents[ent_id] = attrs
                self.evidence_log.append({
                    "id": ent_id,
                    "title": attrs.get("title"),
                    "source_id": attrs.get("source_id"),
                    "ingested_at": event.timestamp,
                })
            elif ent_type == "contradiction":
                self.contradictions[ent_id] = attrs
            elif ent_type == "finding":
                self.findings[ent_id] = attrs
            elif ent_type == "evidence_request":
                self.evidence_requests[ent_id] = attrs
