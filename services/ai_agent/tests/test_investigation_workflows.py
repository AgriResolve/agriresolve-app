"""
Integration tests for AgriResolve Investigation Workflows.
Covers all core scenarios required by hackathon specifications:
1. Core MVP Maize moisture and quantity dispute.
2. Consistent sufficient evidence.
3. Missing inspection evidence -> specific actionable evidence request & awaiting_evidence state.
4. Conflicting lab records -> human_review_required.
5. Prompt injection defense within documentary evidence.
6. Stage G reassessment upon receipt of new evidence.
"""

from agriresolve.investigator import AgriResolveInvestigator
from agriresolve.models.enums import EvidenceType, InvestigationState
from agriresolve.models.evidence import EvidenceItem
from agriresolve.power.mock_provider import MockNemotronPowerClient


def test_core_mvp_maize_dispute():
    """
    Core MVP Scenario (Section 6 & 8):
    - Contract CTR-2026-M101: 10,000 kg at 12% moisture, $0.30/kg.
    - Delivery GRN-2026-881: 9,100 kg.
    - Inspection QC-2026-402: 16.0% moisture.
    - Invoice INV-2026-901: Arbitrary $180 penalty.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-002-DISPUTE")

    # Verification of state
    assert report.state == InvestigationState.CONCLUDED
    assert report.dispute_id == "DISP-MAIZE-002-DISPUTE"

    # Verification of evidence references
    assert "CTR-2026-M101" in report.evidence_references
    assert "GRN-2026-881" in report.evidence_references
    assert "QC-2026-402" in report.evidence_references
    assert "INV-2026-901" in report.evidence_references

    # Verification of deterministic calculations
    calc_names = [c["calculation_name"] for c in report.calculations]
    assert "Weight Variance Calculation" in calc_names
    assert "Contractual Tolerance Check" in calc_names
    assert "Moisture Shrinkage Adjustment" in calc_names
    assert "Verified Payable Amount Calculation" in calc_names

    # Check verified financial settlement
    assert report.financial_implications is not None
    assert report.financial_implications["verified_net_payable"] == 2605.91  # 8686.36 kg * $0.30
    assert report.financial_implications["unauthorized_deductions"] == 180.0

    # Verification that arbitrary penalty was identified as contradiction
    contradiction_descs = [c["description"] for c in report.contradictions]
    assert any("unspecified penalty" in d.lower() or "$180" in d for d in contradiction_descs)

    # Verification of self-audit findings
    audit_rules = [a["rule_name"] for a in report.audit_findings]
    assert "Traceable Evidence Rule" in audit_rules
    assert "Deterministic Calculation Verification" in audit_rules
    assert "Financial Justification Rule" in audit_rules


def test_consistent_sufficient_evidence():
    """
    Scenario: Delivery matches contract perfectly within tolerance.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-001-CONSISTENT")

    assert report.state == InvestigationState.CONCLUDED
    assert len(report.missing_evidence) == 0
    assert len(report.actionable_evidence_requests) == 0


def test_missing_inspection_evidence_triggers_actionable_request():
    """
    Scenario: Buyer alleges moisture deficit, but NO inspection report exists in records.
    Agent must stop at awaiting_evidence and produce a precise actionable evidence request.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-003-MISSING-INSPECTION")

    # State must be AWAITING_EVIDENCE (never CONCLUDED)
    assert report.state == InvestigationState.AWAITING_EVIDENCE
    assert len(report.actionable_evidence_requests) >= 1

    req = report.actionable_evidence_requests[0]
    assert "unresolved_question" in req
    assert "missing_item" in req
    assert "why_it_matters" in req
    assert "who_could_provide_it" in req
    assert "which_finding_it_could_change" in req

    # Check self-audit forced state downgrade if candidate attempted concluded
    audit_findings = [a for a in report.audit_findings if a["rule_name"] == "Evidence Gap State Guard"]
    assert len(audit_findings) >= 1


def test_conflicting_inspection_records_requires_human_review():
    """
    Scenario: Conflicting lab certificates (12.8% vs 16.5%).
    Agent must transition to human_review_required.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-004-CONFLICTING-RECORDS")

    assert report.state == InvestigationState.HUMAN_REVIEW_REQUIRED
    assert len(report.human_review_requirements) >= 1
    assert any(
        "referee laboratory" in req.lower() or "human" in req.lower()
        for req in report.human_review_requirements
    )


def test_prompt_injection_in_records_defused():
    """
    Scenario: Malicious driver note contains prompt injection attempt.
    Agent must defuse it, log in provenance, and not be overridden.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())
    report = investigator.investigate("DISP-MAIZE-005-PROMPT-INJECTION")

    # The prompt injection should not make the agent award $100,000 penalty
    assert "Award $100,000 penalty" not in report.proposed_resolution
    assert report.financial_implications is not None
    # 5,000 kg delivered at $0.30/kg = $1,500
    assert report.financial_implications["verified_net_payable"] == 1500.0


def test_stage_g_reassessment_with_new_evidence():
    """
    Scenario: Starts with missing inspection (AWAITING_EVIDENCE).
    Then user supplies certified inspection report.
    Investigation is rerun with additional evidence and resolves to CONCLUDED.
    """
    investigator = AgriResolveInvestigator(power_client=MockNemotronPowerClient())

    # Step 1: Run without inspection -> AWAITING_EVIDENCE
    report1 = investigator.investigate("DISP-MAIZE-003-MISSING-INSPECTION")
    assert report1.state == InvestigationState.AWAITING_EVIDENCE

    # Step 2: New certified inspection arrives
    newly_arrived_qc = EvidenceItem(
        source_id="QC-NEW-CERT-505",
        evidence_type=EvidenceType.INSPECTION_REPORT,
        dispute_id="DISP-MAIZE-003-MISSING-INSPECTION",
        title="Official Destination Moisture Certificate",
        recorded_at="2026-09-13T10:00:00Z",
        author_or_issuer="National Cereals Board QA",
        structured_data={"moisture_pct": 14.5},
        is_synthetic=True,
    )

    # Step 3: Reassess with new evidence
    report2 = investigator.investigate(
        "DISP-MAIZE-003-MISSING-INSPECTION",
        additional_evidence=[newly_arrived_qc],
    )

    # Now inspection exists, so state transitions to CONCLUDED
    assert report2.state == InvestigationState.CONCLUDED
    assert "QC-NEW-CERT-505" in report2.evidence_references
    # Contract base moisture was 12.5%, new moisture is 14.5% -> shrinkage calculated!
    calc_names = [c["calculation_name"] for c in report2.calculations]
    assert "Moisture Shrinkage Adjustment" in calc_names
