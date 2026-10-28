"""
Tests for Meterless World Model Specification Conformance in AgriResolve.
Covers:
1. Stable, content-addressed deterministic IDs.
2. Mandatory provenance and checksum validation.
3. Append-only canonical store & view rebuildability.
4. Lineage tracing from derived findings back to source evidence documents.
5. Ingest of new evidence updating dispute state without erasing previous evidence or provenance.
"""

from datetime import datetime, timezone
import pytest
from agriresolve.investigator import AgriResolveInvestigator
from agriresolve.models.enums import EvidenceType, InvestigationState
from agriresolve.models.evidence import EvidenceItem
from agriresolve.power.mock_provider import MockNemotronPowerClient
from agriresolve.world_model.engine import WorldModel, WorldModelError
from agriresolve.world_model.stable_id import (
    compute_content_checksum,
    compute_stable_context_id,
    compute_stable_entity_id,
    compute_stable_relationship_id,
)
from agriresolve.world_model.types import Provenance


def test_stable_id_determinism_and_content_addressing():
    """
    Specification: IDs are deterministic, content-addressable, and never renumbered.
    Same input -> Same ID.
    """
    id1 = compute_stable_entity_id("evidence_document", "CTR-2026-M101")
    id2 = compute_stable_entity_id("evidence_document", "ctr-2026-m101")
    id3 = compute_stable_entity_id("evidence_document", "  CTR-2026-M101  ")
    assert id1 == id2 == id3
    assert id1.startswith("evidence_document:")

    rel1 = compute_stable_relationship_id("ent_a", "supports", "ent_b", "ctx_1")
    rel2 = compute_stable_relationship_id("ent_a", "supports", "ent_b", "ctx_1")
    assert rel1 == rel2
    assert rel1.startswith("rel_")


def test_mandatory_provenance_enforced():
    """
    Specification: Every record gets a Provenance block. No provenance -> reject.
    """
    wm = WorldModel()
    with pytest.raises(WorldModelError) as exc:
        wm.upsert_entity(
            entity_type="evidence_document",
            canonical_key="CTR-999",
            attrs={"text": "arbitrary"},
            provenance=None,  # type: ignore
        )
    assert "Provenance is mandatory" in str(exc.value)


def test_canonical_store_append_only_and_view_rebuildability():
    """
    Specification: The canonical store is the source of truth.
    Every view can be thrown away and rebuilt from the event log.
    """
    wm = WorldModel()
    ctx_id = wm.upsert_context("dispute", "DISP-TEST-001", {"title": "Test Dispute"})

    prov = Provenance(
        source_id="CTR-001",
        source_type="contract",
        recorded_at=datetime.now(timezone.utc).isoformat(),
        checksum=compute_content_checksum({"terms": "10000kg"}),
    )
    doc_id = wm.upsert_entity("evidence_document", "CTR-001", {"quantity": 10000}, prov, context_id=ctx_id)
    rel_id = wm.relate(doc_id, "governs", ctx_id, context_id=ctx_id)

    # Initial view state
    assert doc_id in wm.graph_view.entities
    assert rel_id in wm.graph_view.relationships
    initial_event_count = wm.store.count()
    assert initial_event_count >= 3

    # Wipe views and rebuild from the canonical event store
    wm.rebuild_views()

    # Verify identical state restored after complete rebuild
    assert doc_id in wm.graph_view.entities
    assert rel_id in wm.graph_view.relationships
    assert wm.graph_view.entities[doc_id].attrs["quantity"] == 10000
    assert wm.graph_view.entities[doc_id].provenance.source_id == "CTR-001"


def test_lineage_trace_from_finding_to_source_evidence():
    """
    Specification: Ensure every derived finding can be traced back to its source evidence.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-002-DISPUTE")

    wm = investigator.world_model
    graph_view = wm.view("graph")

    # Locate finding entities in the graph view
    finding_entities = [e for e in graph_view.entities.values() if e.type == "finding"]
    assert len(finding_entities) >= 3

    # Test Q1 finding lineage
    q1_finding = next(e for e in finding_entities if e.attrs.get("question_id") == "Q1")
    traced_sources = graph_view.trace_provenance(q1_finding.id)
    traced_source_ids = {s.attrs.get("source_id") for s in traced_sources}

    # Q1 was established by GRN-2026-881 and CTR-2026-M101
    assert "GRN-2026-881" in traced_source_ids
    assert "CTR-2026-M101" in traced_source_ids

    # Test Q2 finding lineage (moisture shrinkage)
    q2_finding = next(e for e in finding_entities if e.attrs.get("question_id") == "Q2")
    q2_sources = {s.attrs.get("source_id") for s in graph_view.trace_provenance(q2_finding.id)}
    assert "QC-2026-402" in q2_sources
    assert "CTR-2026-M101" in q2_sources


def test_new_evidence_updates_state_without_erasing_previous_evidence_or_provenance():
    """
    Specification: New evidence updates the dispute state without erasing
    previous evidence, observations, or provenance.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())

    # Step 1: Run dispute with missing inspection evidence
    report1 = investigator.investigate("DISP-MAIZE-003-MISSING-INSPECTION")
    assert report1.state == InvestigationState.AWAITING_EVIDENCE

    wm = investigator.world_model
    initial_event_count = wm.store.count()
    initial_entities = dict(wm.graph_view.entities)

    # Verify initial evidence documents exist
    ctr_entity_id = compute_stable_entity_id("evidence_document", "CTR-003")
    grn_entity_id = compute_stable_entity_id("evidence_document", "GRN-003")
    assert ctr_entity_id in initial_entities
    assert grn_entity_id in initial_entities

    initial_ctr_provenance = initial_entities[ctr_entity_id].provenance
    assert initial_ctr_provenance.source_id == "CTR-003"

    # Step 2: New certified inspection evidence arrives
    new_qc = EvidenceItem(
        source_id="QC-NEW-CERT-505",
        evidence_type=EvidenceType.INSPECTION_REPORT,
        dispute_id="DISP-MAIZE-003-MISSING-INSPECTION",
        title="Official Destination Moisture Certificate",
        recorded_at="2026-09-13T10:00:00Z",
        author_or_issuer="National Cereals Board QA",
        structured_data={"moisture_pct": 14.5},
        is_synthetic=True,
    )

    # Step 3: Reassess dispute with new evidence
    report2 = investigator.investigate(
        "DISP-MAIZE-003-MISSING-INSPECTION",
        additional_evidence=[new_qc],
    )

    # 1. State successfully updated
    assert report2.state == InvestigationState.CONCLUDED

    # 2. Event log is append-only: event count strictly increased
    assert wm.store.count() > initial_event_count

    # 3. Previous evidence documents still exist and were NOT erased or corrupted
    updated_entities = wm.graph_view.entities
    assert ctr_entity_id in updated_entities
    assert grn_entity_id in updated_entities
    assert updated_entities[ctr_entity_id].provenance.source_id == initial_ctr_provenance.source_id
    assert updated_entities[ctr_entity_id].provenance.checksum == initial_ctr_provenance.checksum

    # 4. New evidence document exists in the graph with full provenance
    qc_entity_id = compute_stable_entity_id("evidence_document", "QC-NEW-CERT-505")
    assert qc_entity_id in updated_entities
    assert updated_entities[qc_entity_id].provenance.source_id == "QC-NEW-CERT-505"
    assert updated_entities[qc_entity_id].attrs["structured_data"]["moisture_pct"] == 14.5

    # 5. Timeline view recorded the state transitions
    state_history = wm.timeline_view.get_state_history()
    to_states = [t["to_state"] for t in state_history]
    assert "investigating" in to_states
    assert "awaiting_evidence" in to_states
    assert "concluded" in to_states

    # 6. Rebuilding views from store preserves entire history
    wm.rebuild_views()
    assert ctr_entity_id in wm.graph_view.entities
    assert qc_entity_id in wm.graph_view.entities
    assert wm.dispute_view.current_state == "concluded"
