"""
Models for Party Claims and Disputed Questions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .enums import DisputeCategory


@dataclass
class PartyClaim:
    """
    An allegation or statement made by one of the disputing parties.
    Must not be accepted as fact without independent documentary evidence.
    """
    party: str  # e.g., "Farmer (Seller)", "GrainCorp (Buyer)"
    claim_text: str
    category: DisputeCategory
    alleged_quantity: Optional[float] = None
    alleged_moisture_pct: Optional[float] = None
    alleged_financial_claim: Optional[float] = None
    alleged_currency: Optional[str] = None
    supporting_doc_references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "party": self.party,
            "claim_text": self.claim_text,
            "category": self.category.value,
            "alleged_quantity": self.alleged_quantity,
            "alleged_moisture_pct": self.alleged_moisture_pct,
            "alleged_financial_claim": self.alleged_financial_claim,
            "alleged_currency": self.alleged_currency,
            "supporting_doc_references": self.supporting_doc_references,
        }


@dataclass
class DisputedQuestion:
    """
    A specific question in dispute that the investigation must answer.
    """
    question_id: str
    question_text: str
    category: DisputeCategory
    required_evidence_categories: List[str]
    status: str = "unresolved"  # "unresolved", "resolved", "partially_resolved"
    findings_summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "category": self.category.value,
            "required_evidence_categories": self.required_evidence_categories,
            "status": self.status,
            "findings_summary": self.findings_summary,
        }
