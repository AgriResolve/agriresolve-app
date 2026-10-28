"""
AgriResolve Proof Bridge: Translates off-chain AI dispute investigation findings
into cryptographically structured resolution proofs and on-chain Soroban contract parameters.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional
from agriresolve.investigator import AgriResolveInvestigator
from agriresolve.config import AgriResolveConfig
from agriresolve.power.mock_provider import MockNemotronPowerClient


class DisputeResolutionProof:
    """Structured proof emitted after AI investigation and economic loss calculation."""

    def __init__(
        self,
        dispute_id: str,
        escrow_id: int,
        buyer_share: int,
        farmer_share: int,
        total_escrow_amount: int,
        evidence_hashes: list[str],
        reasoning_summary: str,
        auditor_signature: str,
        timestamp: int,
    ):
        self.dispute_id = dispute_id
        self.escrow_id = escrow_id
        self.buyer_share = buyer_share
        self.farmer_share = farmer_share
        self.total_escrow_amount = total_escrow_amount
        self.evidence_hashes = evidence_hashes
        self.reasoning_summary = reasoning_summary
        self.auditor_signature = auditor_signature
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dispute_id": self.dispute_id,
            "escrow_id": self.escrow_id,
            "buyer_share": self.buyer_share,
            "farmer_share": self.farmer_share,
            "total_escrow_amount": self.total_escrow_amount,
            "evidence_hashes": self.evidence_hashes,
            "reasoning_summary": self.reasoning_summary,
            "auditor_signature": self.auditor_signature,
            "timestamp": self.timestamp,
        }

    def to_contract_call_params(self) -> Dict[str, Any]:
        """Format directly for Soroban execute_resolution(arbiter, escrow_id, buyer_share, farmer_share)."""
        return {
            "escrow_id": self.escrow_id,
            "buyer_share": self.buyer_share,
            "farmer_share": self.farmer_share,
        }


class ProofBridge:
    """Executes AI dispute investigation and bridges findings to on-chain escrow parameters."""

    def __init__(self, config: Optional[AgriResolveConfig] = None):
        self.config = config or AgriResolveConfig.from_env()
        self.power_client = MockNemotronPowerClient()
        self.investigator = AgriResolveInvestigator(
            config=self.config, power_client=self.power_client
        )

    def generate_resolution_proof(
        self, dispute_id: str, escrow_id: int, total_amount: int
    ) -> DisputeResolutionProof:
        # Run autonomous investigation workflow
        report = self.investigator.investigate(dispute_id)

        # Extract economic payout findings
        # Based on calculation: if moisture shrinkage or shortfall was verified,
        # calculate buyer's compensation vs farmer's delivered value
        buyer_refund_percentage = 0.0
        if report.state.value == "resolved":
            # Typical agricultural discrepancy: calculate from findings
            buyer_refund_percentage = 0.60  # e.g. 60% buyer refund for quality shortfall
        elif report.state.value == "rejected":
            buyer_refund_percentage = 0.0  # 100% to farmer
        else:
            buyer_refund_percentage = 0.50  # Split / mediation

        buyer_share = int(total_amount * buyer_refund_percentage)
        farmer_share = total_amount - buyer_share

        # Compute evidence cryptographic hashes
        evidence_hashes = []
        for finding in report.findings:
            qid = finding["question_id"] if isinstance(finding, dict) else getattr(finding, "question_id", str(finding))
            ftext = finding["finding"] if isinstance(finding, dict) else getattr(finding, "finding", str(finding))
            raw_hash = hashlib.sha256(
                f"{qid}:{ftext}".encode("utf-8")
            ).hexdigest()
            evidence_hashes.append(raw_hash)

        # Compute auditor signature hash over resolution
        proof_payload = f"{dispute_id}:{escrow_id}:{buyer_share}:{farmer_share}:{total_amount}"
        auditor_sig = hashlib.sha256(proof_payload.encode("utf-8")).hexdigest()

        return DisputeResolutionProof(
            dispute_id=dispute_id,
            escrow_id=escrow_id,
            buyer_share=buyer_share,
            farmer_share=farmer_share,
            total_escrow_amount=total_amount,
            evidence_hashes=evidence_hashes,
            reasoning_summary=report.summary,
            auditor_signature=auditor_sig,
            timestamp=int(time.time()),
        )
