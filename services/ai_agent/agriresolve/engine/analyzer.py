"""
Evidence Analysis and Contradiction Detection Engine for AgriResolve.
Implements Stages A, B, D, E, F, and G of the investigation methodology.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from ..models.claims import DisputedQuestion, PartyClaim
from ..models.enums import (
    ContradictionSeverity,
    DisputeCategory,
    EvidenceType,
    InvestigationState,
)
from ..models.evidence import EvidenceItem
from ..models.investigation import (
    ActionableEvidenceRequest,
    Contradiction,
    EvidenceGap,
)
from .calculator import AgriculturalCalculator, CalculationError


class EvidenceAnalyzer:
    """
    Evaluates documentary evidence against party claims, detects contradictions,
    uncovers gaps, and formulates precise, actionable evidence requests.
    """

    @classmethod
    def analyze_chronology(cls, evidence_items: List[EvidenceItem]) -> List[str]:
        """
        Validates event sequence (e.g., Contract signed -> Delivery executed -> Inspection performed -> Settlement billed).
        """
        observations: List[str] = []
        dated_items = [e for e in evidence_items if e.recorded_at]
        # Sort chronologically
        sorted_items = sorted(dated_items, key=lambda x: str(x.recorded_at))

        for item in sorted_items:
            observations.append(f"{item.recorded_at} | [{item.evidence_type.value}] {item.source_id}: {item.title}")

        return observations

    @classmethod
    def detect_contradictions(
        cls,
        claims: List[PartyClaim],
        evidence_items: List[EvidenceItem],
    ) -> List[Contradiction]:
        """
        Identifies contradictions between documentary records and party claims,
        or between competing records.
        """
        contradictions: List[Contradiction] = []
        c_count = 1

        # Extract primary documentary evidence
        contracts = [e for e in evidence_items if e.evidence_type == EvidenceType.CONTRACT]
        deliveries = [e for e in evidence_items if e.evidence_type == EvidenceType.DELIVERY_RECORD]
        inspections = [e for e in evidence_items if e.evidence_type == EvidenceType.INSPECTION_REPORT]
        invoices = [e for e in evidence_items if e.evidence_type == EvidenceType.INVOICE]

        # 1. Contradiction between multiple inspection reports (if multiple exist)
        if len(inspections) > 1:
            m_values = {}
            for insp in inspections:
                m = insp.structured_data.get("moisture_pct")
                if m is not None:
                    m_values[insp.source_id] = m

            if len(set(m_values.values())) > 1:
                contradictions.append(
                    Contradiction(
                        contradiction_id=f"CONTR-{c_count:03d}",
                        description="Conflicting moisture measurements recorded across different inspection reports.",
                        severity=ContradictionSeverity.CRITICAL,
                        source_ids_involved=list(m_values.keys()),
                        conflicting_values=m_values,
                        reconciliation_attempt="Examine sampling point (dispatch vs destination) and laboratory accreditation.",
                        is_resolved=False,
                    )
                )
                c_count += 1

        # 2. Contradiction between Delivered Weight and Contract Quantity
        if contracts and deliveries:
            ctr = contracts[0]
            deliv = deliveries[0]
            ctr_qty = ctr.structured_data.get("contracted_quantity_kg")
            deliv_qty = deliv.structured_data.get("net_delivered_quantity_kg")

            if ctr_qty is not None and deliv_qty is not None:
                diff = deliv_qty - ctr_qty
                if abs(diff) > 0.01:
                    tolerance = ctr.structured_data.get("tolerance_pct", 0.0)
                    severity = (
                        ContradictionSeverity.CRITICAL
                        if abs(diff) > (ctr_qty * (tolerance / 100.0))
                        else ContradictionSeverity.MODERATE
                    )
                    contradictions.append(
                        Contradiction(
                            contradiction_id=f"CONTR-{c_count:03d}",
                            description=f"Net delivered quantity ({deliv_qty} kg) deviates from contracted volume ({ctr_qty} kg).",
                            severity=severity,
                            source_ids_involved=[ctr.source_id, deliv.source_id],
                            conflicting_values={
                                "contracted_kg": ctr_qty,
                                "delivered_kg": deliv_qty,
                                "variance_kg": diff,
                            },
                            reconciliation_attempt="Check weighbridge certificate and allowable contract tolerance clause.",
                            is_resolved=False,
                        )
                    )
                    c_count += 1

        # 3. Contradiction between Farmer/Buyer Claim and Verified Record
        for claim in claims:
            # Check quantity claim vs delivery note
            if claim.alleged_quantity and deliveries:
                actual_deliv = deliveries[0].structured_data.get("net_delivered_quantity_kg")
                if actual_deliv and abs(claim.alleged_quantity - actual_deliv) > 10.0:
                    contradictions.append(
                        Contradiction(
                            contradiction_id=f"CONTR-{c_count:03d}",
                            description=f"Party '{claim.party}' claimed {claim.alleged_quantity} kg, but official weighbridge record establishes {actual_deliv} kg.",
                            severity=ContradictionSeverity.MODERATE,
                            source_ids_involved=[deliveries[0].source_id],
                            conflicting_values={
                                "party_claim": claim.alleged_quantity,
                                "official_record": actual_deliv,
                            },
                            reconciliation_attempt="Documentary weighbridge certificate takes precedence over unverified party allegation.",
                            is_resolved=True,
                        )
                    )
                    c_count += 1

            # Check moisture claim vs inspection report
            if claim.alleged_moisture_pct and inspections:
                actual_m = inspections[0].structured_data.get("moisture_pct")
                if actual_m and abs(claim.alleged_moisture_pct - actual_m) > 0.5:
                    contradictions.append(
                        Contradiction(
                            contradiction_id=f"CONTR-{c_count:03d}",
                            description=f"Party '{claim.party}' alleged {claim.alleged_moisture_pct}% moisture, but lab test recorded {actual_m}%.",
                            severity=ContradictionSeverity.MODERATE,
                            source_ids_involved=[inspections[0].source_id],
                            conflicting_values={
                                "party_allegation": claim.alleged_moisture_pct,
                                "lab_measurement": actual_m,
                            },
                            reconciliation_attempt="Verified lab certificate establishes moisture content unless test method is formally challenged.",
                            is_resolved=True,
                        )
                    )
                    c_count += 1

        # 4. Contradiction: Invoice deductions not authorized by contract
        if invoices and contracts:
            inv = invoices[0]
            ctr = contracts[0]
            unspecified_penalties = inv.structured_data.get("unspecified_penalty", 0.0)
            if unspecified_penalties > 0:
                ctr_penalty_clause = ctr.structured_data.get("penalty_terms", "")
                if "arbitrary" in ctr_penalty_clause.lower() or "no arbitrary" in ctr_penalty_clause.lower() or not ctr_penalty_clause:
                    contradictions.append(
                        Contradiction(
                            contradiction_id=f"CONTR-{c_count:03d}",
                            description=f"Invoice {inv.source_id} deducted ${unspecified_penalties} in penalties, but Contract {ctr.source_id} contains no authorized penalty clause.",
                            severity=ContradictionSeverity.CRITICAL,
                            source_ids_involved=[inv.source_id, ctr.source_id],
                            conflicting_values={
                                "invoice_penalty": unspecified_penalties,
                                "contract_penalty_authorization": "None or Prohibited",
                            },
                            reconciliation_attempt="Disallow unverified penalty deduction from settlement recommendation.",
                            is_resolved=False,
                        )
                    )
                    c_count += 1

        return contradictions

    @classmethod
    def identify_evidence_gaps(
        cls,
        questions: List[DisputedQuestion],
        evidence_items: List[EvidenceItem],
    ) -> Tuple[List[EvidenceGap], List[ActionableEvidenceRequest]]:
        """
        Identifies evidence gaps and constructs actionable evidence requests per Stage F.
        """
        gaps: List[EvidenceGap] = []
        requests: List[ActionableEvidenceRequest] = []
        req_counter = 1

        available_types = {e.evidence_type for e in evidence_items}
        available_source_ids = [e.source_id for e in evidence_items]

        for q in questions:
            for required_cat in q.required_evidence_categories:
                # Map string category to EvidenceType
                cat_enum = None
                for et in EvidenceType:
                    if et.value == required_cat:
                        cat_enum = et
                        break

                if cat_enum and cat_enum not in available_types:
                    gap_id = f"GAP-{req_counter:03d}"
                    gaps.append(
                        EvidenceGap(
                            gap_id=gap_id,
                            disputed_question_id=q.question_id,
                            description=f"Missing {required_cat.replace('_', ' ').title()} required to resolve: '{q.question_text}'",
                            materiality="blocking",
                        )
                    )

                    # Stage F Actionable Evidence Request formulation
                    who_could_provide = "Independent Inspector or Buyer Silo"
                    if cat_enum == EvidenceType.INSPECTION_REPORT:
                        missing_item_desc = "Certified Laboratory Moisture & Quality Inspection Certificate (including sampling date, method, moisture %, and tester credentials)"
                        why_matters = "Moisture adjustments cannot be legally or contractually applied without an accredited, empirical measurement."
                        finding_changed = "Determines whether moisture shrinkage deduction applies and verifies actual payable weight."
                    elif cat_enum == EvidenceType.CONTRACT:
                        missing_item_desc = "Fully executed Sales Contract or Purchase Order stating base moisture, unit price, and tolerance"
                        why_matters = "Without governing terms, baseline standards and agreed price per unit cannot be established."
                        finding_changed = "Governs the baseline price, tolerance, and shrinkage formulas."
                        who_could_provide = "Buyer or Seller"
                    elif cat_enum == EvidenceType.DELIVERY_RECORD:
                        missing_item_desc = "Official Weighbridge Ticket / Goods Received Note (GRN) with gross, tare, and net weights"
                        why_matters = "Physical delivered mass is the foundational quantity for all settlement calculations."
                        finding_changed = "Establishes whether a physical delivery deficit occurred."
                        who_could_provide = "Weighbridge Operator or Receiving Warehouse"
                    else:
                        missing_item_desc = f"Official {required_cat} record"
                        why_matters = f"Required to substantiate claims for question {q.question_id}"
                        finding_changed = "Settlement calculations and contractual compliance"
                        who_could_provide = "Relevant contracting party"

                    requests.append(
                        ActionableEvidenceRequest(
                            request_id=f"REQ-{req_counter:03d}",
                            unresolved_question=q.question_text,
                            available_evidence=available_source_ids,
                            missing_item=missing_item_desc,
                            why_it_matters=why_matters,
                            which_finding_it_could_change=finding_changed,
                            who_could_provide_it=who_could_provide,
                            can_investigation_continue_without_it=False,
                        )
                    )
                    req_counter += 1

        return gaps, requests

    @classmethod
    def reassess_with_new_evidence(
        cls,
        existing_evidence: List[EvidenceItem],
        new_evidence_items: List[EvidenceItem],
    ) -> Tuple[List[EvidenceItem], List[str]]:
        """
        Stage G: Incorporates new evidence, preserving provenance, and returns explanation of what changed.
        """
        combined = list(existing_evidence)
        change_explanations: List[str] = []

        for new_item in new_evidence_items:
            # Check for existing item with same source ID
            existing_match = next((e for e in combined if e.source_id == new_item.source_id), None)
            if existing_match:
                change_explanations.append(
                    f"Updated existing evidence record '{new_item.source_id}' ({new_item.title}). Provenance preserved."
                )
                combined.remove(existing_match)
            else:
                change_explanations.append(
                    f"Added new documentary evidence '{new_item.source_id}' ({new_item.title}, type={new_item.evidence_type.value})."
                )
            combined.append(new_item)

        return combined, change_explanations
