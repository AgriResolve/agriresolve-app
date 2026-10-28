# AgriResolve: AI Evidence & Dispute Investigation Pipeline (`services/ai_agent`)

> Autonomous agricultural dispute investigation engine with Meterless World Model provenance and Soroban contract proof generation.

## Architecture

```
Disputed Trade Evidence (Weighbridge tickets, Moisture certs, Invoices)
                       │
                       ▼
          ┌───────────────────────────┐
          │  Meterless World Model    │ ◄── Graph of claims, bounds & evidence
          └────────────┬──────────────┘
                       │
                       ▼
          ┌───────────────────────────┐
          │  Llama-3.1-Nemotron Agent │ ◄── Reconciles contradictions & applies rules
          └────────────┬──────────────┘
                       │
                       ▼
          ┌───────────────────────────┐
          │   Dispute Proof Bridge    │ ◄── Computes split payout & SHA-256 auditor proof
          └────────────┬──────────────┘
                       │
                       ▼
      On-Chain Settlement `execute_resolution(arbiter, escrow_id, buyer_share, farmer_share)`
```

## Running Demonstration

```bash
# Run CLI demonstration on dispute test scenarios
python3 demo.py --scenario DISP-MAIZE-002-DISPUTE

# Run HTTP server for web dashboard integration
python3 server.py
```
