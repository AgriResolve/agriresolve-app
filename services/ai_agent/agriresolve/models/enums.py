"""
Domain Enums for AgriResolve Investigation Agent.
"""

from enum import Enum


class InvestigationState(str, Enum):
    """
    Explicit investigation states required by AgriResolve specification:
    - investigating: evidence is still being gathered or checked.
    - awaiting_evidence: a specific additional document, measurement, or clarification is required.
    - provisional_finding: the evidence supports a tentative conclusion, but material uncertainty remains.
    - concluded: the available evidence supports a defensible finding within the stated scope.
    - human_review_required: a decision or assessment outside the agent's permitted capabilities is necessary.
    """
    INVESTIGATING = "investigating"
    AWAITING_EVIDENCE = "awaiting_evidence"
    PROVISIONAL_FINDING = "provisional_finding"
    CONCLUDED = "concluded"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class DisputeCategory(str, Enum):
    QUANTITY = "quantity"
    MOISTURE_QUALITY = "moisture_quality"
    PRICING_ADJUSTMENT = "pricing_adjustment"
    DELIVERY_CONDITION = "delivery_condition"
    CONTRACTUAL_COMPLIANCE = "contractual_compliance"


class EvidenceType(str, Enum):
    CONTRACT = "contract"
    DELIVERY_RECORD = "delivery_record"
    INSPECTION_REPORT = "inspection_report"
    INVOICE = "invoice"
    COMMUNICATION = "communication"
    STANDARD = "standard"


class ContradictionSeverity(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    MINOR = "minor"


class UnitOfMeasure(str, Enum):
    KG = "kg"
    MT = "MT"
    PERCENT = "%"
    USD = "USD"
    KES = "KES"
    LOCAL_CURRENCY = "currency"
