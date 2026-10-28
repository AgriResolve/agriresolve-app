"""
Controlled evidence retrieval and calculation tools for AgriResolve.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from ..adapters.fixtures import SyntheticFixtureRepository
from ..adapters.zetaris import ZetarisAdapter
from ..engine.calculator import AgriculturalCalculator, CalculationError
from ..models.enums import EvidenceType
from ..models.evidence import EvidenceItem
from ..security.guardrails import DisputeGuardrail, SecurityError
from ..security.sanitizer import EvidenceSanitizer
from .base import BaseTool, ToolResult


class ScopedEvidenceRetrievalTool(BaseTool):
    """
    Controlled tool for retrieving evidence scoped strictly to the dispute.
    """

    def __init__(
        self,
        name: str,
        description: str,
        evidence_type: EvidenceType,
        zetaris_adapter: Optional[ZetarisAdapter] = None,
        fixture_provider: Optional[Callable[[str], Optional[Dict]]] = None,
    ):
        self.name = name
        self.description = description
        self.evidence_type = evidence_type
        self.zetaris_adapter = zetaris_adapter
        self.fixture_provider = fixture_provider or SyntheticFixtureRepository.get_dispute_bundle

    def execute(self, dispute_id: str, **kwargs) -> ToolResult:
        try:
            valid_id = DisputeGuardrail.validate_dispute_id(dispute_id)
        except SecurityError as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))

        evidence_found: List[EvidenceItem] = []

        # 1. Check live Zetaris adapter if configured
        if self.zetaris_adapter and self.zetaris_adapter.config.is_configured:
            try:
                all_evidence = self.zetaris_adapter.fetch_dispute_evidence(valid_id)
                evidence_found = [e for e in all_evidence if e.evidence_type == self.evidence_type]
            except Exception as e:
                return ToolResult(tool_name=self.name, success=False, error=f"Zetaris error: {e}")
        else:
            # 2. Check synthetic test fixtures
            bundle = self.fixture_provider(valid_id)
            if bundle and "evidence" in bundle:
                evidence_found = [
                    e for e in bundle["evidence"] if e.evidence_type == self.evidence_type
                ]

        # Sanitize any raw content in returned evidence
        sanitized_dicts = []
        for item in evidence_found:
            defused_content, was_flagged, patterns = EvidenceSanitizer.inspect_and_defuse(item.raw_content)
            item.raw_content = defused_content
            if was_flagged:
                item.add_provenance(f"Security Alert: Defused suspicious prompt injection pattern: {patterns}")
            sanitized_dicts.append(item.to_dict())

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=sanitized_dicts,
            metadata={"count": len(sanitized_dicts), "evidence_type": self.evidence_type.value},
        )


class CalculateMoistureShrinkageTool(BaseTool):
    """
    Controlled tool for performing deterministic moisture shrinkage calculations.
    """
    name = "calculate_moisture_shrinkage"
    description = "Calculates moisture shrinkage and adjusted weight using the standard Minary formula."

    def execute(
        self,
        delivered_weight_kg: float,
        actual_moisture_pct: float,
        contract_base_moisture_pct: float,
        handling_loss_pct: float = 0.0,
        source_term_ref: str = "Contractual Minary Shrinkage Clause",
        **kwargs,
    ) -> ToolResult:
        try:
            step = AgriculturalCalculator.calculate_moisture_shrinkage(
                delivered_weight_kg=float(delivered_weight_kg),
                actual_moisture_pct=float(actual_moisture_pct),
                contract_base_moisture_pct=float(contract_base_moisture_pct),
                handling_loss_pct=float(handling_loss_pct),
                source_term_ref=source_term_ref,
            )
            return ToolResult(tool_name=self.name, success=True, data=step.to_dict())
        except (CalculationError, ValueError) as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))


class CalculateWeightVarianceTool(BaseTool):
    """
    Controlled tool for computing weight variance between contract and delivery.
    """
    name = "calculate_weight_variance"
    description = "Calculates weight variance in kilograms between contracted and delivered mass."

    def execute(
        self,
        contract_qty: float,
        contract_unit: str,
        delivered_qty: float,
        delivered_unit: str,
        source_term_ref: str = "Delivery Specification",
        **kwargs,
    ) -> ToolResult:
        try:
            step = AgriculturalCalculator.calculate_weight_variance(
                contract_qty=float(contract_qty),
                contract_unit=str(contract_unit),
                delivered_qty=float(delivered_qty),
                delivered_unit=str(delivered_unit),
                source_term_ref=source_term_ref,
            )
            return ToolResult(tool_name=self.name, success=True, data=step.to_dict())
        except (CalculationError, ValueError) as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))
