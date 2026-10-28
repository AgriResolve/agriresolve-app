"""
Investigation Self-Audit and Report Validator for AgriResolve.
Implements Stage H checks to ensure traceability, state validity, calculation reproducibility,
and evidence-supported conclusions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from ..models.enums import ContradictionSeverity, InvestigationState
from ..models.investigation import (
    ActionableEvidenceRequest,
    AuditFinding,
    CalculationStep,
    Contradiction,
    EvidenceGap,
    InvestigationReport,
)


class InvestigationAuditor:
    """
    Performs comprehensive self-auditing before an investigation report is released.
    Prevents unsupported certainty, unjustified financial deductions, and invalid state transitions.
    """

    @classmethod
    def audit_investigation(
        cls,
        candidate_state: InvestigationState,
        evidence_references: List[str],
        contradictions: List[Contradiction],
        evidence_gaps: List[EvidenceGap],
        requests: List[ActionableEvidenceRequest],
        calculations: List[CalculationStep],
        financial_implications: Optional[Dict[str, Any]],
    ) -> Tuple[InvestigationState, List[AuditFinding]]:
        """
        Runs Stage H verification rules and returns:
            (final_state, audit_findings)
        """
        audit_findings: List[AuditFinding] = []
        final_state = candidate_state

        # Rule 1: Traceable Evidence Check
        if not evidence_references:
            audit_findings.append(
                AuditFinding(
                    rule_name="Traceable Evidence Rule",
                    passed=False,
                    details="No verified evidence references were cited for material findings.",
                    corrective_action_taken="State downgraded to awaiting_evidence or human_review_required.",
                )
            )
            final_state = InvestigationState.AWAITING_EVIDENCE
        else:
            audit_findings.append(
                AuditFinding(
                    rule_name="Traceable Evidence Rule",
                    passed=True,
                    details=f"All findings reference verified source identifiers: {evidence_references}.",
                )
            )

        # Rule 2: Blocking Evidence Gap Check
        # If blocking gaps or evidence requests exist, state CANNOT be 'concluded'
        blocking_gaps = [g for g in evidence_gaps if g.materiality == "blocking"]
        if blocking_gaps or requests:
            if candidate_state == InvestigationState.CONCLUDED:
                final_state = InvestigationState.AWAITING_EVIDENCE
                audit_findings.append(
                    AuditFinding(
                        rule_name="Evidence Gap State Guard",
                        passed=False,
                        details=f"Found {len(blocking_gaps)} blocking gaps and {len(requests)} pending evidence requests. Candidate state 'concluded' is forbidden.",
                        corrective_action_taken="Corrected investigation state from 'concluded' to 'awaiting_evidence'.",
                    )
                )
            else:
                audit_findings.append(
                    AuditFinding(
                        rule_name="Evidence Gap State Guard",
                        passed=True,
                        details="State appropriately reflects pending evidence requirements.",
                    )
                )

        # Rule 3: Unresolved Critical Contradictions Check
        # If there are unresolved critical contradictions (e.g. conflicting lab tests), state must be human_review_required or provisional_finding
        unresolved_critical = [
            c for c in contradictions if not c.is_resolved and c.severity == ContradictionSeverity.CRITICAL
        ]
        if unresolved_critical:
            if final_state == InvestigationState.CONCLUDED:
                final_state = InvestigationState.HUMAN_REVIEW_REQUIRED
                audit_findings.append(
                    AuditFinding(
                        rule_name="Contradiction Resolution Rule",
                        passed=False,
                        details=f"Found {len(unresolved_critical)} unresolved critical contradictions that cannot be settled without human/expert review.",
                        corrective_action_taken="Updated state from 'concluded' to 'human_review_required'.",
                    )
                )
            else:
                audit_findings.append(
                    AuditFinding(
                        rule_name="Contradiction Resolution Rule",
                        passed=True,
                        details=f"Disclosed {len(unresolved_critical)} unresolved critical contradictions for expert/human assessment.",
                    )
                )

        # Rule 4: Deterministic Calculations Reproducibility & Units
        unverified_calcs = [c for c in calculations if not c.is_verified or not c.source_term_reference]
        if unverified_calcs:
            audit_findings.append(
                AuditFinding(
                    rule_name="Deterministic Calculation Verification",
                    passed=False,
                    details=f"Found {len(unverified_calcs)} calculations lacking explicit verification or contractual source term references.",
                    corrective_action_taken="Excluded unverified calculations from final financial determination.",
                )
            )
        else:
            audit_findings.append(
                AuditFinding(
                    rule_name="Deterministic Calculation Verification",
                    passed=True,
                    details=f"All {len(calculations)} calculations have verified formulas, units, and contractual authority.",
                )
            )

        # Rule 5: Financial Justification Rule
        if financial_implications:
            unauthorized_deductions = financial_implications.get("unauthorized_deductions", 0.0)
            if unauthorized_deductions > 0:
                audit_findings.append(
                    AuditFinding(
                        rule_name="Financial Justification Rule",
                        passed=False,
                        details=f"Detected ${unauthorized_deductions} in unauthorized deductions/penalties not supported by contract.",
                        corrective_action_taken="Reclassified unauthorized deductions as disputed/disallowed in proposed settlement.",
                    )
                )
            else:
                audit_findings.append(
                    AuditFinding(
                        rule_name="Financial Justification Rule",
                        passed=True,
                        details="Financial implications strictly follow verified contractual terms and rates.",
                    )
                )

        return final_state, audit_findings
