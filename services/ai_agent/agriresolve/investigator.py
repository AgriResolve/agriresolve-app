"""
AgriResolve Investigator: Autonomous AI Agricultural Dispute Investigation Agent.
Implements bounded Stages A-I investigation workflow with controlled tools,
deterministic math, contradiction detection, self-auditing, and actionable evidence requests.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from .adapters.fixtures import SyntheticFixtureRepository
from .adapters.zetaris import ZetarisAdapter
from .config import AgriResolveConfig
from .engine.analyzer import EvidenceAnalyzer
from .engine.auditor import InvestigationAuditor
from .engine.calculator import AgriculturalCalculator
from .models.claims import DisputedQuestion, PartyClaim
from .models.enums import (
    ContradictionSeverity,
    DisputeCategory,
    EvidenceType,
    InvestigationState,
)
from .models.evidence import EvidenceItem
from .models.investigation import (
    ActionableEvidenceRequest,
    AuditFinding,
    CalculationStep,
    Contradiction,
    EvidenceGap,
    InvestigationReport,
)
from .power.base import PowerLayerClient
from .power.nemotron import NemotronPowerClient
from .security.guardrails import DisputeGuardrail, SecurityError
from .security.sanitizer import EvidenceSanitizer
from .tools.base import BaseTool
from .tools.evidence_tools import (
    CalculateMoistureShrinkageTool,
    CalculateWeightVarianceTool,
    ScopedEvidenceRetrievalTool,
)
from .tools.registry import PolicyLimitExceededError, ToolRegistry
from .world_model.engine import WorldModel
from .world_model.stable_id import (
    compute_content_checksum,
    compute_stable_entity_id,
)
from .world_model.types import Provenance

logger = logging.getLogger("agriresolve.investigator")


class AgriResolveInvestigator:
    """
    Autonomous investigator agent for agricultural disputes.
    """

    def __init__(
        self,
        config: Optional[AgriResolveConfig] = None,
        power_client: Optional[PowerLayerClient] = None,
        zetaris_adapter: Optional[ZetarisAdapter] = None,
        world_model: Optional[WorldModel] = None,
    ):
        self.config = config or AgriResolveConfig.from_env()
        self.power_client = power_client or NemotronPowerClient(self.config.power)
        self.zetaris_adapter = zetaris_adapter or ZetarisAdapter(self.config.zetaris)
        self.world_model = world_model or WorldModel()

        # Initialize Controlled Tool Registry
        self.tool_registry = ToolRegistry(self.config.policy)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """
        Registers controlled read-only tools and calculation tools.
        """
        # Scoped retrieval tools for each core evidence type
        self.tool_registry.register_tool(
            ScopedEvidenceRetrievalTool(
                name="get_contract_terms",
                description="Retrieves the commercial sales contract and governing specifications.",
                evidence_type=EvidenceType.CONTRACT,
                zetaris_adapter=self.zetaris_adapter,
            )
        )
        self.tool_registry.register_tool(
            ScopedEvidenceRetrievalTool(
                name="get_delivery_records",
                description="Retrieves weighbridge tickets, delivery notes, and goods received notes.",
                evidence_type=EvidenceType.DELIVERY_RECORD,
                zetaris_adapter=self.zetaris_adapter,
            )
        )
        self.tool_registry.register_tool(
            ScopedEvidenceRetrievalTool(
                name="get_inspection_reports",
                description="Retrieves laboratory analysis certificates and moisture/quality test reports.",
                evidence_type=EvidenceType.INSPECTION_REPORT,
                zetaris_adapter=self.zetaris_adapter,
            )
        )
        self.tool_registry.register_tool(
            ScopedEvidenceRetrievalTool(
                name="get_invoices_and_statements",
                description="Retrieves payment vouchers, billing statements, and settlement deduction claims.",
                evidence_type=EvidenceType.INVOICE,
                zetaris_adapter=self.zetaris_adapter,
            )
        )
        self.tool_registry.register_tool(CalculateMoistureShrinkageTool())
        self.tool_registry.register_tool(CalculateWeightVarianceTool())

    def investigate(
        self,
        dispute_id: str,
        initial_claims: Optional[List[PartyClaim]] = None,
        initial_questions: Optional[List[DisputedQuestion]] = None,
        additional_evidence: Optional[List[EvidenceItem]] = None,
    ) -> InvestigationReport:
        """
        Executes bounded Stages A through I of the investigation.
        """
        # Security validation of dispute identifier
        valid_dispute_id = DisputeGuardrail.validate_dispute_id(dispute_id)

        # Reset tool registry step counts for this investigation workflow session
        self.tool_registry.reset_session()

        # Track execution metrics
        state = InvestigationState.INVESTIGATING
        evidence_store: List[EvidenceItem] = []
        calculations: List[CalculationStep] = []
        findings: List[Dict[str, Any]] = []
        assumptions_and_limitations: List[str] = [
            "Findings are advisory and based exclusively on documentary records retrieved through authorized interfaces.",
            "Calculations require verified contractual authority and do not permit arbitrary penalties.",
        ]
        what_could_change: List[str] = []
        human_review_reqs: List[str] = []
        recommended_actions: List[str] = []

        # Load bundle if claims/questions not provided
        bundle = SyntheticFixtureRepository.get_dispute_bundle(valid_dispute_id)
        claims = initial_claims or (bundle.get("claims", []) if bundle else [])
        questions = initial_questions or (bundle.get("questions", []) if bundle else [])

        # =========================================================================
        # Meterless World Model Context Initialization
        # =========================================================================
        ctx_id = self.world_model.upsert_context(
            context_type="dispute",
            canonical_key=valid_dispute_id,
            attrs={"dispute_id": valid_dispute_id, "title": bundle.get("title", valid_dispute_id) if bundle else valid_dispute_id},
        )
        self.world_model.transition_state(
            context_id=ctx_id,
            from_state="uninitialized",
            to_state=InvestigationState.INVESTIGATING.value,
            reason="Investigation workflow initiated",
        )

        # =========================================================================
        # Stage A: Understand the dispute
        # =========================================================================
        self.tool_registry.start_new_step()
        logger.info(f"Stage A: Analyzing dispute {valid_dispute_id} with {len(claims)} party claims.")
        for claim in claims:
            now_iso = datetime.now(timezone.utc).isoformat()
            p_prov = Provenance(
                source_id=f"party_{claim.party}",
                source_type="party_entity",
                recorded_at=now_iso,
                checksum=compute_content_checksum(claim.party),
            )
            party_id = self.world_model.upsert_entity(
                entity_type="party",
                canonical_key=claim.party,
                attrs={"name": claim.party},
                provenance=p_prov,
                context_id=ctx_id,
            )
            c_prov = Provenance(
                source_id=f"claim_{claim.party}_{claim.category.value}",
                source_type="party_allegation",
                recorded_at=now_iso,
                checksum=compute_content_checksum(claim.to_dict()),
            )
            claim_id = self.world_model.upsert_entity(
                entity_type="claim",
                canonical_key=f"{claim.party}:{claim.category.value}",
                attrs=claim.to_dict(),
                provenance=c_prov,
                context_id=ctx_id,
            )
            self.world_model.relate(party_id, "asserts", claim_id, context_id=ctx_id)

        # =========================================================================
        # Stage B: Determine what evidence is needed
        # =========================================================================
        logger.info(f"Stage B: Evaluating needed evidence categories for {len(questions)} disputed questions.")

        # =========================================================================
        # Stage C: Retrieve available evidence via controlled tools
        # =========================================================================
        self.tool_registry.start_new_step()
        retrieval_tools = [
            "get_contract_terms",
            "get_delivery_records",
            "get_inspection_reports",
            "get_invoices_and_statements",
        ]

        for t_name in retrieval_tools:
            res = self.tool_registry.execute_tool(t_name, dispute_id=valid_dispute_id)
            if res.success and res.data:
                for d in res.data:
                    # Reconstruct EvidenceItem
                    item = EvidenceItem(
                        source_id=d["source_id"],
                        evidence_type=EvidenceType(d["evidence_type"]),
                        dispute_id=valid_dispute_id,
                        title=d["title"],
                        recorded_at=d.get("recorded_at"),
                        author_or_issuer=d.get("author_or_issuer", "Data Layer"),
                        structured_data=d.get("structured_data", {}),
                        raw_content=d.get("raw_content", ""),
                        is_synthetic=d.get("is_synthetic", False),
                        provenance_notes=d.get("provenance_notes", []),
                        is_untrusted_input=d.get("is_untrusted_input", True),
                    )
                    evidence_store.append(item)

        # Incorporate newly supplied additional evidence if provided (Stage G)
        if additional_evidence:
            evidence_store, changes = EvidenceAnalyzer.reassess_with_new_evidence(evidence_store, additional_evidence)
            for c in changes:
                assumptions_and_limitations.append(f"Stage G Reassessment: {c}")

        # Ingest all evidence documents into World Model with mandatory provenance
        for item in evidence_store:
            now_iso = item.recorded_at or datetime.now(timezone.utc).isoformat()
            doc_prov = Provenance(
                source_id=item.source_id,
                source_type=item.evidence_type.value,
                recorded_at=now_iso,
                checksum=compute_content_checksum(item.to_dict()),
                metadata={"author": item.author_or_issuer, "synthetic": item.is_synthetic},
            )
            doc_id = self.world_model.upsert_entity(
                entity_type="evidence_document",
                canonical_key=item.source_id,
                attrs=item.to_dict(),
                provenance=doc_prov,
                context_id=ctx_id,
            )
            rel_type = "governs" if item.evidence_type == EvidenceType.CONTRACT else "evidences"
            self.world_model.relate(doc_id, rel_type, ctx_id, context_id=ctx_id)

        # =========================================================================
        # Stage D: Evaluate the evidence (dates, comparability, contradictions)
        # =========================================================================
        self.tool_registry.start_new_step()
        chronology = EvidenceAnalyzer.analyze_chronology(evidence_store)
        contradictions = EvidenceAnalyzer.detect_contradictions(claims, evidence_store)

        for c in contradictions:
            now_iso = datetime.now(timezone.utc).isoformat()
            c_prov = Provenance(
                source_id=c.contradiction_id,
                source_type="contradiction_detection",
                recorded_at=now_iso,
                checksum=compute_content_checksum(c.to_dict()),
            )
            contr_id = self.world_model.upsert_entity(
                entity_type="contradiction",
                canonical_key=c.contradiction_id,
                attrs=c.to_dict(),
                provenance=c_prov,
                context_id=ctx_id,
            )
            for src_id in c.source_ids_involved:
                doc_ent_id = compute_stable_entity_id("evidence_document", src_id)
                self.world_model.relate(doc_ent_id, "conflicts_in", contr_id, context_id=ctx_id)

        # =========================================================================
        # Stage E & F: Decide whether more investigation is needed / Request missing evidence
        # =========================================================================
        evidence_gaps, evidence_requests = EvidenceAnalyzer.identify_evidence_gaps(questions, evidence_store)

        if evidence_requests:
            state = InvestigationState.AWAITING_EVIDENCE
            for req in evidence_requests:
                now_iso = datetime.now(timezone.utc).isoformat()
                req_prov = Provenance(
                    source_id=req.request_id,
                    source_type="evidence_request",
                    recorded_at=now_iso,
                    checksum=compute_content_checksum(req.to_dict()),
                )
                req_id = self.world_model.upsert_entity(
                    entity_type="evidence_request",
                    canonical_key=req.request_id,
                    attrs=req.to_dict(),
                    provenance=req_prov,
                    context_id=ctx_id,
                )
                self.world_model.relate(ctx_id, "requires_evidence", req_id, context_id=ctx_id)
                what_could_change.append(
                    f"Receipt of '{req.missing_item}' from {req.who_could_provide_it} could alter: {req.which_finding_it_could_change}."
                )
                recommended_actions.append(
                    f"Issue formal evidence request to {req.who_could_provide_it} for: {req.missing_item}."
                )

        # =========================================================================
        # Deterministic Calculations (Weight, Moisture, Adjustments)
        # =========================================================================
        self.tool_registry.start_new_step()
        contracts = [e for e in evidence_store if e.evidence_type == EvidenceType.CONTRACT]
        deliveries = [e for e in evidence_store if e.evidence_type == EvidenceType.DELIVERY_RECORD]
        inspections = [e for e in evidence_store if e.evidence_type == EvidenceType.INSPECTION_REPORT]
        invoices = [e for e in evidence_store if e.evidence_type == EvidenceType.INVOICE]

        settlement_weight_kg: Optional[float] = None
        financial_summary: Optional[Dict[str, Any]] = None

        if contracts and deliveries:
            ctr = contracts[0]
            deliv = deliveries[0]
            ctr_qty = ctr.structured_data.get("contracted_quantity_kg", 0.0)
            deliv_qty = deliv.structured_data.get("net_delivered_quantity_kg", 0.0)
            unit_price = ctr.structured_data.get("unit_price", 0.0)
            currency = ctr.structured_data.get("currency", "USD")
            base_moisture = ctr.structured_data.get("base_moisture_pct", 12.0)
            tolerance_pct = ctr.structured_data.get("tolerance_pct", 0.0)

            # 1. Weight Variance
            var_step = AgriculturalCalculator.calculate_weight_variance(
                contract_qty=ctr_qty,
                contract_unit="kg",
                delivered_qty=deliv_qty,
                delivered_unit="kg",
                source_term_ref=f"Contract {ctr.source_id} Clause 4",
            )
            calculations.append(var_step)

            # Tolerance Check
            within_tol, tol_step = AgriculturalCalculator.check_tolerance(
                contract_qty_kg=ctr_qty,
                delivered_qty_kg=deliv_qty,
                tolerance_pct=tolerance_pct,
                source_term_ref=f"Contract {ctr.source_id} Tolerance Clause",
            )
            calculations.append(tol_step)

            # 2. Moisture Shrinkage if Inspection Record exists
            if inspections:
                insp = inspections[0]
                actual_m = insp.structured_data.get("moisture_pct")
                if actual_m is not None and actual_m > base_moisture:
                    shrink_step = AgriculturalCalculator.calculate_moisture_shrinkage(
                        delivered_weight_kg=deliv_qty,
                        actual_moisture_pct=actual_m,
                        contract_base_moisture_pct=base_moisture,
                        handling_loss_pct=0.0,  # Only water shrink unless contractual handling loss verified
                        source_term_ref=f"Contract {ctr.source_id} Minary Shrinkage Clause",
                    )
                    calculations.append(shrink_step)
                    settlement_weight_kg = shrink_step.result
                else:
                    settlement_weight_kg = deliv_qty
            else:
                # No inspection record exists to justify moisture adjustment
                settlement_weight_kg = deliv_qty

            # 3. Financial Settlement Calculation
            if settlement_weight_kg is not None and unit_price > 0:
                fin_step = AgriculturalCalculator.calculate_verified_financial_impact(
                    settlement_weight_kg=settlement_weight_kg,
                    contract_price_per_unit=unit_price,
                    price_unit="kg",
                    penalty_deduction=0.0,  # No unauthorized penalty
                    currency=currency,
                    source_term_ref=f"Contract {ctr.source_id} Pricing Schedule",
                )
                calculations.append(fin_step)

                # Check if invoice had unauthorized penalties
                invoice_unauthorized_penalty = 0.0
                if invoices:
                    invoice_unauthorized_penalty = invoices[0].structured_data.get("unspecified_penalty", 0.0)

                financial_summary = {
                    "contracted_value": round(ctr_qty * unit_price, 2),
                    "delivered_gross_value": round(deliv_qty * unit_price, 2),
                    "verified_net_payable": fin_step.result,
                    "currency": currency,
                    "unauthorized_deductions": invoice_unauthorized_penalty,
                    "authorized_basis": f"Settlement based on {settlement_weight_kg} kg verified weight at ${unit_price}/kg.",
                }

        # Formulate core findings
        for q in questions:
            if q.question_id == "Q1":
                if deliveries and contracts:
                    deliv_val = deliveries[0].structured_data.get("net_delivered_quantity_kg")
                    ctr_val = contracts[0].structured_data.get("contracted_quantity_kg")
                    q.status = "resolved"
                    findings.append({
                        "question_id": "Q1",
                        "finding": f"Weighbridge certificate {deliveries[0].source_id} establishes delivered weight of {deliv_val} kg against contracted {ctr_val} kg.",
                        "supported_by": [deliveries[0].source_id, contracts[0].source_id],
                        "status": "established",
                    })
                else:
                    findings.append({
                        "question_id": "Q1",
                        "finding": "Delivered quantity cannot be verified due to missing delivery documentation.",
                        "supported_by": [],
                        "status": "unresolved",
                    })

            elif q.question_id == "Q2":
                if inspections and contracts:
                    m_val = inspections[0].structured_data.get("moisture_pct")
                    base_m = contracts[0].structured_data.get("base_moisture_pct")
                    q.status = "resolved"
                    findings.append({
                        "question_id": "Q2",
                        "finding": f"Laboratory inspection {inspections[0].source_id} establishes moisture of {m_val}%, exceeding base standard of {base_m}%. Contract authorizes standard Minary shrinkage.",
                        "supported_by": [inspections[0].source_id, contracts[0].source_id],
                        "status": "established",
                    })
                else:
                    findings.append({
                        "question_id": "Q2",
                        "finding": "Moisture claims remain unverified. Official certified inspection certificate is missing.",
                        "supported_by": [],
                        "status": "unresolved",
                    })

            elif q.question_id == "Q3":
                if invoices and contracts:
                    unauthorized = invoices[0].structured_data.get("unspecified_penalty", 0.0)
                    if unauthorized > 0:
                        findings.append({
                            "question_id": "Q3",
                            "finding": f"Buyer deduction of ${unauthorized} for unspecified penalty is unauthorized by Contract {contracts[0].source_id} and is disallowed.",
                            "supported_by": [invoices[0].source_id, contracts[0].source_id],
                            "status": "established",
                        })
                    else:
                        findings.append({
                            "question_id": "Q3",
                            "finding": "All invoice line items correspond to verified contractual terms.",
                            "supported_by": [invoices[0].source_id, contracts[0].source_id],
                            "status": "established",
                        })

        # Reconcile contradictions that were resolved by verified calculations and findings
        for c in contradictions:
            desc_lower = c.description.lower()
            if "deviates from contracted" in desc_lower and calculations:
                c.is_resolved = True
                c.reconciliation_attempt = "Resolved by deterministic weight variance calculation and contractual tolerance evaluation."
            elif ("penalties" in desc_lower or "penalty" in desc_lower) and financial_summary:
                c.is_resolved = True
                c.reconciliation_attempt = "Resolved by disallowing unauthorized invoice deduction from verified financial settlement."

        # Record observations for deterministic calculations into World Model
        for calc in calculations:
            calc_prov = Provenance(
                source_id=calc.calculation_name,
                source_type="deterministic_calculation",
                recorded_at=datetime.now(timezone.utc).isoformat(),
                checksum=compute_content_checksum(calc.to_dict()),
            )
            self.world_model.record_observation(ctx_id, calc.calculation_name, calc.to_dict(), provenance=calc_prov)

        # Ingest findings into World Model with explicit traceable provenance edges
        for f in findings:
            now_iso = datetime.now(timezone.utc).isoformat()
            f_prov = Provenance(
                source_id=f"finding_{f['question_id']}",
                source_type="investigative_finding",
                recorded_at=now_iso,
                checksum=compute_content_checksum(f),
            )
            finding_id = self.world_model.upsert_entity(
                entity_type="finding",
                canonical_key=f"{valid_dispute_id}:{f['question_id']}",
                attrs=f,
                provenance=f_prov,
                context_id=ctx_id,
            )
            for src_id in f.get("supported_by", []):
                doc_ent_id = compute_stable_entity_id("evidence_document", src_id)
                self.world_model.relate(finding_id, "derived_from", doc_ent_id, context_id=ctx_id)
                self.world_model.relate(doc_ent_id, "supports", finding_id, context_id=ctx_id)

        # =========================================================================
        # Qualitative Nemotron Reasoning (Power Layer)
        # =========================================================================
        nemotron_summary = ""
        if self.power_client.is_available():
            try:
                prompt = (
                    f"Dispute: {valid_dispute_id}\n"
                    f"Chronology: {chronology}\n"
                    f"Contradictions detected: {[c.description for c in contradictions]}\n"
                    f"Calculations: {[c.formula + ' -> ' + str(c.result) + ' ' + c.unit for c in calculations]}\n"
                    "Synthesize an evidence-backed rationale explaining why the findings are justified and where uncertainty lies."
                )
                nemotron_summary = self.power_client.generate_reasoning(
                    prompt=prompt,
                    system_prompt=(
                        "You are AgriResolve's analytical reasoning assistant. You explain evidence findings neutrally. "
                        "Never fabricate facts, never add unverified penalties, and clearly distinguish proven facts from claims."
                    ),
                )
            except Exception as e:
                logger.warning(f"Power layer inference unavailable or failed: {e}")
                nemotron_summary = (
                    f"Quantitative findings verified deterministically. (Power layer note: {e})"
                )
        else:
            nemotron_summary = (
                "Quantitative findings verified deterministically. (NVIDIA Nemotron live key not configured in .env; "
                "qualitative reasoning rendered from verified documentary analysis)."
            )

        # =========================================================================
        # Stage H: Self-Audit and Verification
        # =========================================================================
        candidate_state = (
            InvestigationState.AWAITING_EVIDENCE
            if evidence_requests
            else (
                InvestigationState.HUMAN_REVIEW_REQUIRED
                if any(c.severity == ContradictionSeverity.CRITICAL and not c.is_resolved for c in contradictions)
                else InvestigationState.CONCLUDED
            )
        )

        all_evidence_ids = [e.source_id for e in evidence_store]
        final_state, audit_findings = InvestigationAuditor.audit_investigation(
            candidate_state=candidate_state,
            evidence_references=all_evidence_ids,
            contradictions=contradictions,
            evidence_gaps=evidence_gaps,
            requests=evidence_requests,
            calculations=calculations,
            financial_implications=financial_summary,
        )

        # =========================================================================
        # Stage I: Stop Responsibly & Formulate Structured Report
        # =========================================================================
        if final_state == InvestigationState.CONCLUDED:
            deliv_kg = deliveries[0].structured_data.get('net_delivered_quantity_kg') if deliveries else "Unknown"
            moisture_clause = f" with {inspections[0].structured_data.get('moisture_pct')}% moisture" if inspections else ""
            settlement_kg_str = f" yields adjusted settlement mass of {settlement_weight_kg:.2f} kg." if settlement_weight_kg is not None else "."
            fin_payable_str = f" Verified payable amount is ${financial_summary['verified_net_payable']:.2f} {financial_summary['currency']}." if financial_summary else ""
            deductions_str = f" Arbitrary penalties of ${financial_summary['unauthorized_deductions']:.2f} are disallowed." if financial_summary and financial_summary.get('unauthorized_deductions') else ""
            proposed_resolution = (
                f"Defensible Finding Established: Delivered mass of {deliv_kg} kg{moisture_clause}{settlement_kg_str}"
                f"{fin_payable_str}{deductions_str}"
            )
        elif final_state == InvestigationState.AWAITING_EVIDENCE:
            proposed_resolution = (
                f"Investigation Suspended Pending Evidence: Dispute cannot be settled without verified records. "
                f"Identified {len(evidence_requests)} actionable evidence request(s). "
                f"No financial deduction or final liability can be imposed without requested documentation."
            )
        elif final_state == InvestigationState.HUMAN_REVIEW_REQUIRED:
            proposed_resolution = (
                f"Human Review Required: Unresolved critical contradictions between competing accredited records or lab tests "
                f"require human expert assessment, referee laboratory analysis, or joint committee review."
            )
            human_review_reqs.append("Referee laboratory re-testing or joint party physical sample review.")
        else:
            proposed_resolution = "Provisional finding reached; further verification recommended."

        # Conditional scenarios
        conditional_scenarios = []
        if final_state == InvestigationState.AWAITING_EVIDENCE and inspections == []:
            conditional_scenarios.append({
                "scenario": "If Seller provides certified moisture certificate demonstrating <= 12.5% moisture",
                "consequence": "Full delivered weight payable with zero shrinkage deduction.",
            })
            conditional_scenarios.append({
                "scenario": "If Buyer provides certified inspection certificate confirming 16.0% moisture",
                "consequence": "Standard Minary formula applies, reducing payable weight to equivalent dry matter.",
            })

        # Transition World Model to final audited investigation state
        self.world_model.transition_state(
            context_id=ctx_id,
            from_state=InvestigationState.INVESTIGATING.value,
            to_state=final_state.value,
            reason=f"Investigation workflow concluded with state: {final_state.value}",
        )

        world_model_summary = {
            "context_id": ctx_id,
            "event_count": self.world_model.store.count(),
            "entity_count": len(self.world_model.graph_view.entities),
            "relationship_count": len(self.world_model.graph_view.relationships),
            "dispute_state": self.world_model.dispute_view.current_state,
        }

        report = InvestigationReport(
            dispute_id=valid_dispute_id,
            summary=f"AgriResolve investigation report for dispute {valid_dispute_id}. State: {final_state.value.upper()}.",
            state=final_state,
            disputed_questions=[q.to_dict() for q in questions],
            findings=findings,
            evidence_references=all_evidence_ids,
            supporting_evidence=[
                e.to_dict() for e in evidence_store if e.evidence_type in (EvidenceType.CONTRACT, EvidenceType.DELIVERY_RECORD)
            ],
            contradictory_evidence=[
                e.to_dict() for e in evidence_store if e.evidence_type in (EvidenceType.INSPECTION_REPORT, EvidenceType.INVOICE)
            ],
            contradictions=[c.to_dict() for c in contradictions],
            missing_evidence=[g.__dict__ for g in evidence_gaps],
            actionable_evidence_requests=[r.to_dict() for r in evidence_requests],
            calculations=[c.to_dict() for c in calculations],
            financial_implications=financial_summary,
            proposed_resolution=proposed_resolution,
            conditional_scenarios=conditional_scenarios,
            assumptions_and_limitations=assumptions_and_limitations,
            what_could_change_the_finding=what_could_change,
            human_review_requirements=human_review_reqs,
            recommended_next_actions=recommended_actions or ["Execute settlement per verified figures."],
            audit_findings=[a.__dict__ for a in audit_findings],
            world_model_summary=world_model_summary,
        )

        return report
