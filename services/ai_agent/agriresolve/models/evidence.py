"""
Evidence domain models for AgriResolve.
Preserves provenance, source identifiers, structured measurements, and synthetic flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .enums import EvidenceType


@dataclass
class EvidenceItem:
    """
    Represents an atomic piece of evidence retrieved from Zetaris or supplied by parties.
    """
    source_id: str
    evidence_type: EvidenceType
    dispute_id: str
    title: str
    recorded_at: Optional[str]
    author_or_issuer: str
    structured_data: Dict[str, Any]
    raw_content: str = ""
    is_synthetic: bool = False
    provenance_notes: List[str] = field(default_factory=list)
    is_untrusted_input: bool = True  # Untrusted by default for security

    def add_provenance(self, note: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        self.provenance_notes.append(f"[{timestamp}] {note}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "evidence_type": self.evidence_type.value,
            "dispute_id": self.dispute_id,
            "title": self.title,
            "recorded_at": self.recorded_at,
            "author_or_issuer": self.author_or_issuer,
            "structured_data": self.structured_data,
            "raw_content": self.raw_content,
            "is_synthetic": self.is_synthetic,
            "provenance_notes": self.provenance_notes,
            "is_untrusted_input": self.is_untrusted_input,
        }
