"""
Investigation state, findings, contradictions, evidence requests, calculations, and report structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .enums import ContradictionSeverity, InvestigationState


@dataclass
class Contradiction:
    """
    Identified conflict between two or more pieces of evidence or between a claim and evidence.
    """
    contradiction_id: str
    description: str
    severity: ContradictionSeverity
    source_ids_involved: List[str]
    conflicting_values: Dict[str, Any]
    reconciliation_attempt: Optional[str] = None
    is_resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contradiction_id": self.contradiction_id,
            "description": self.description,
            "severity": self.severity.value,
            "source_ids_involved": self.source_ids_involved,
            "conflicting_values": self.conflicting_values,
            "reconciliation_attempt": self.reconciliation_attempt,
            "is_resolved": self.is_resolved,
        }


@dataclass
class EvidenceGap:
    """
    An identified gap in the available evidence that prevents conclusive determination.
    """
    gap_id: str
    disputed_question_id: str
    description: str
    materiality: str  # e.g., "blocking", "substantial", "minor"


@dataclass
class ActionableEvidenceRequest:
    """
    Specific, actionable request for missing evidence per Stage F specification:
    - unresolved_question: The question in dispute that cannot be answered
    - available_evidence: What is already documented
    - missing_item: What exactly is missing
    - why_it_matters: Why the missing item is critical
    - which_finding_it_could_change: The specific finding or calculation affected
    - who_could_provide_it: Reasonable party or institution (e.g. Inspector, Buyer, Farmer)
    - can_investigation_continue_without_it: Whether work can proceed conditionally
    """
    request_id: str
    unresolved_question: str
    available_evidence: List[str]
    missing_item: str
    why_it_matters: str
    which_finding_it_could_change: str
    who_could_provide_it: str
    can_investigation_continue_without_it: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "unresolved_question": self.unresolved_question,
            "available_evidence": self.available_evidence,
            "missing_item": self.missing_item,
            "why_it_matters": self.why_it_matters,
            "which_finding_it_could_change": self.which_finding_it_could_change,
            "who_could_provide_it": self.who_could_provide_it,
            "can_investigation_continue_without_it": self.can_investigation_continue_without_it,
        }


@dataclass
class CalculationStep:
    """
    Deterministic calculation step with inputs, units, formula, and verification.
    """
    calculation_name: str
    formula: str
    inputs: Dict[str, Any]
    result: float
    unit: str
    source_term_reference: str  # Contract clause or standard authorizing this formula
    is_verified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calculation_name": self.calculation_name,
            "formula": self.formula,
            "inputs": self.inputs,
            "result": self.result,
            "unit": self.unit,
            "source_term_reference": self.source_term_reference,
            "is_verified": self.is_verified,
        }


@dataclass
class AuditFinding:
    """
    Result of self-audit check run before finalizing a report.
    """
    rule_name: str
    passed: bool
    details: str
    corrective_action_taken: Optional[str] = None


@dataclass
class InvestigationReport:
    """
    Complete structured investigation report per Section 8 specification.
    """
    dispute_id: str
    summary: str
    state: InvestigationState
    disputed_questions: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    evidence_references: List[str]
    supporting_evidence: List[Dict[str, Any]]
    contradictory_evidence: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    missing_evidence: List[Dict[str, Any]]
    actionable_evidence_requests: List[Dict[str, Any]]
    calculations: List[Dict[str, Any]]
    financial_implications: Optional[Dict[str, Any]]
    proposed_resolution: str
    conditional_scenarios: List[Dict[str, Any]]
    assumptions_and_limitations: List[str]
    what_could_change_the_finding: List[str]
    human_review_requirements: List[str]
    recommended_next_actions: List[str]
    audit_findings: List[Dict[str, Any]] = field(default_factory=list)
    world_model_summary: Optional[Dict[str, Any]] = None
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dispute_id": self.dispute_id,
            "summary": self.summary,
            "state": self.state.value,
            "disputed_questions": self.disputed_questions,
            "findings": self.findings,
            "evidence_references": self.evidence_references,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "contradictions": self.contradictions,
            "missing_evidence": self.missing_evidence,
            "actionable_evidence_requests": self.actionable_evidence_requests,
            "calculations": self.calculations,
            "financial_implications": self.financial_implications,
            "proposed_resolution": self.proposed_resolution,
            "conditional_scenarios": self.conditional_scenarios,
            "assumptions_and_limitations": self.assumptions_and_limitations,
            "what_could_change_the_finding": self.what_could_change_the_finding,
            "human_review_requirements": self.human_review_requirements,
            "recommended_next_actions": self.recommended_next_actions,
            "audit_findings": self.audit_findings,
            "world_model_summary": self.world_model_summary,
            "generated_at": self.generated_at,
        }
