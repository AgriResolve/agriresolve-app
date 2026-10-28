"""
AgriResolve CLI Demonstration Script.
Demonstrates the autonomous investigation agent on agricultural dispute scenarios:
- DISP-MAIZE-002-DISPUTE: Core MVP (Quantity shortfall, moisture shrinkage, disallowed penalty)
- DISP-MAIZE-003-MISSING-INSPECTION: Actionable Evidence Request demo
- DISP-MAIZE-004-CONFLICTING-RECORDS: Conflicting inspection certs -> Human Review Required
- DISP-MAIZE-005-PROMPT-INJECTION: Prompt Injection Defense demo
"""

from __future__ import annotations

import argparse
import json
import sys
from agriresolve.config import AgriResolveConfig
from agriresolve.investigator import AgriResolveInvestigator
from agriresolve.power.mock_provider import MockNemotronPowerClient
from agriresolve.power.nemotron import NemotronPowerClient


def render_banner():
    print("=" * 80)
    print("  AGRIRESOLVE: Autonomous AI Agricultural Dispute Investigation Agent")
    print("  Open Agent Hackathon 2026 | Role 1: Agent & Power Lead")
    print("=" * 80)


def print_report(rep_dict: dict):
    print(f"\n[DISPUTE CASE] : {rep_dict['dispute_id']}")
    print(f"[STATUS/STATE] : {rep_dict['state'].upper()}")
    print(f"[SUMMARY]      : {rep_dict['summary']}")
    print("-" * 80)

    print("\n1. DISPUTED QUESTIONS & INVESTIGATIVE FINDINGS:")
    for f in rep_dict["findings"]:
        print(f"  * [{f['question_id']}] Status: {f['status'].upper()}")
        print(f"    Finding: {f['finding']}")
        print(f"    Evidence Provenance: {f['supported_by']}")

    print("\n2. CONTRADICTIONS DETECTED & RECONCILED:")
    for c in rep_dict["contradictions"]:
        res_str = "[RECONCILED]" if c["is_resolved"] else "[UNRESOLVED / CRITICAL]"
        print(f"  * {res_str} {c['contradiction_id']} ({c['severity'].upper()}): {c['description']}")
        if c.get("reconciliation_attempt"):
            print(f"    Action: {c['reconciliation_attempt']}")

    if rep_dict["actionable_evidence_requests"]:
        print("\n3. ACTIONABLE EVIDENCE REQUESTS (Stage F):")
        for req in rep_dict["actionable_evidence_requests"]:
            print(f"  * Request ID: {req['request_id']}")
            print(f"    Target Party: {req['who_could_provide_it']}")
            print(f"    Missing Item: {req['missing_item']}")
            print(f"    Why It Matters: {req['why_it_matters']}")
            print(f"    Impact on Finding: {req['which_finding_it_could_change']}")

    print("\n4. DETERMINISTIC CALCULATIONS (Zero Hallucination Arithmetic):")
    for calc in rep_dict["calculations"]:
        print(f"  * {calc['calculation_name']}")
        print(f"    Formula: {calc['formula']}")
        print(f"    Inputs : {calc['inputs']}")
        print(f"    Result : {calc['result']} {calc['unit']} (Authorized by: {calc['source_term_reference']})")

    if rep_dict.get("financial_implications"):
        fin = rep_dict["financial_implications"]
        print("\n5. FINANCIAL IMPLICATIONS:")
        print(f"  * Contracted Value    : ${fin['contracted_value']} {fin['currency']}")
        print(f"  * Delivered Value     : ${fin['delivered_gross_value']} {fin['currency']}")
        print(f"  * Verified Net Payable: ${fin['verified_net_payable']} {fin['currency']}")
        if fin.get("unauthorized_deductions", 0) > 0:
            print(f"  * Disallowed Deductions: ${fin['unauthorized_deductions']} {fin['currency']} (Unauthorized arbitrary penalty)")

    print("\n6. PROPOSED ADVISORY RESOLUTION:")
    print(f"  {rep_dict['proposed_resolution']}")

    if rep_dict.get("conditional_scenarios"):
        print("\n7. CONDITIONAL RESOLUTION SCENARIOS:")
        for s in rep_dict["conditional_scenarios"]:
            print(f"  * {s['scenario']} -> {s['consequence']}")

    if rep_dict.get("human_review_requirements"):
        print("\n8. HUMAN REVIEW REQUIREMENTS:")
        for hr in rep_dict["human_review_requirements"]:
            print(f"  * {hr}")

    print("\n9. SELF-AUDIT VERIFICATION (Stage H):")
    for audit in rep_dict["audit_findings"]:
        badge = "[PASS]" if audit["passed"] else "[FLAGGED/CORRECTED]"
        print(f"  * {badge} {audit['rule_name']}: {audit['details']}")

    if rep_dict.get("world_model_summary"):
        wm = rep_dict["world_model_summary"]
        print("\n10. METERLESS WORLD MODEL PROJECTION (Official Spec):")
        print(f"  * Context ID           : {wm['context_id']}")
        print(f"  * Total Logged Events  : {wm['event_count']} (Append-Only Canonical Store)")
        print(f"  * Total Graph Entities : {wm['entity_count']} (Content-Addressed Stable IDs)")
        print(f"  * Total Relationships  : {wm['relationship_count']} (Scoped Typed Edges)")
        print(f"  * Reconstructible State: {wm['dispute_state'].upper()}")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Run AgriResolve autonomous agricultural dispute investigator.")
    parser.add_argument(
        "--dispute-id",
        default="DISP-MAIZE-002-DISPUTE",
        help="Dispute ID to investigate (default: DISP-MAIZE-002-DISPUTE)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON investigation report",
    )
    args = parser.parse_args()

    config = AgriResolveConfig.from_env()

    # If NVIDIA credentials are not configured, use MockNemotronPowerClient for offline demonstration
    if config.power.is_configured:
        power_client = NemotronPowerClient(config.power)
        power_mode = "Live NVIDIA NIM / Meterless Nemotron"
    else:
        power_client = MockNemotronPowerClient()
        power_mode = "Offline Deterministic Engine (NVIDIA_API_KEY not set in .env)"

    investigator = AgriResolveInvestigator(config=config, power_client=power_client)

    if not args.json:
        render_banner()
        print(f"Power Layer Mode: {power_mode}")
        print(f"Investigating Dispute: {args.dispute_id}...")

    report = investigator.investigate(args.dispute_id)
    rep_dict = report.to_dict()

    if args.json:
        print(json.dumps(rep_dict, indent=2))
    else:
        print_report(rep_dict)


if __name__ == "__main__":
    main()
