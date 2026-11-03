# AgriResolve Application Workspace (`AgriResolve-app`)

## 🌍 Live Ecosystem & Resources
* **Web App:** [https://agrires.vercel.app/](https://agrires.vercel.app/)
* **Documentation Site:** [https://agriresolve.github.io/agriresolve-docs/](https://agriresolve.github.io/agriresolve-docs/)
* **API / Indexer:** [https://agriresolve-app.onrender.com/health](https://agriresolve-app.onrender.com/health)
* **Demo Video:** [Watch on Google Drive](https://drive.google.com/file/d/19gYJMcZit6NssLxwmhBllQecmnPoG_F8/view)

[![CI Status](https://github.com/AgriResolve/AgriResolve-app/actions/workflows/ci.yml/badge.svg)](https://github.com/AgriResolve/AgriResolve-app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stellar Protocol](https://img.shields.io/badge/Stellar-Protocol%2022%20%2F%2029-blue.svg)](https://stellar.org/)
[![Soroban SDK](https://img.shields.io/badge/Soroban%20SDK-v22%20%2F%20v29-brightgreen.svg)](https://soroban.stellar.org/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15.1-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)

Full-stack agricultural trade escrow interface, official TypeScript Soroban SDK, and automated AI Arbiter Oracle backend for the **AgriResolve Protocol** on the Stellar network.

---

## Deployed Stellar Testnet Contracts

The application workspace connects directly to live smart contracts deployed and initialized on Stellar Testnet:

| Contract Name | Contract ID | Explorer Link | Status |
|---|---|---|---|
| `agriresolve-registry` | `CC3OJZP4DCYOOTRJTT66UHMAGR2677JNDBNFQYMREQA2ONDWNRAO75J6` | [View on Stellar.Expert](https://stellar.expert/explorer/testnet/contract/CC3OJZP4DCYOOTRJTT66UHMAGR2677JNDBNFQYMREQA2ONDWNRAO75J6) | Active |
| `agriresolve-escrow` | `CCPZFPNUQGNT5O6H3VWT2H23CLXF2POF5QYDAD4HPOB2RRKSHO63OIXC` | [View on Stellar.Expert](https://stellar.expert/explorer/testnet/contract/CCPZFPNUQGNT5O6H3VWT2H23CLXF2POF5QYDAD4HPOB2RRKSHO63OIXC) | Active |
| `agriresolve-dispute` | `CCBQBMQFQPRRMOQLPNYSIBGTL7AOXXQAAIADXE2YYTZHSUSDS6Z4ES5N` | [View on Stellar.Expert](https://stellar.expert/explorer/testnet/contract/CCBQBMQFQPRRMOQLPNYSIBGTL7AOXXQAAIADXE2YYTZHSUSDS6Z4ES5N) | Active |

---

## Monorepo Architecture

This repository is structured as a zero-Rust pnpm monorepo containing three core components:

```text
AgriResolve-app/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions for SDK, Web, and Indexer
├── packages/
│   └── sdk/                        # @agriresolve/sdk: Official TypeScript SDK
│       ├── src/
│       │   ├── index.ts
│       │   ├── types.ts            # Contract types & error enums
│       │   ├── xdr.ts              # ScVal encoding and sha256 helpers
│       │   ├── registryClient.ts   # Participant & commodity spec RPC calls
│       │   ├── escrowClient.ts     # Escrow trade lifecycle & split settlement
│       │   └── disputeClient.ts    # Evidence submission & resolution bridge
│       └── test/                   # SDK unit tests
├── apps/
│   └── web/                        # Next.js 15 (App Router) + Tailwind CSS
│       ├── src/
│       │   ├── app/
│       │   │   ├── page.tsx        # Non-jargon Farmer-First Landing Page
│       │   │   ├── signup/page.tsx # 2-Role Sign-Up (Farmer & Buyer ONLY)
│       │   │   └── dashboard/page.tsx # Utilitarian B2B Escrow & Evidence Dashboard
│       │   ├── components/
│       │   │   ├── Navbar.tsx
│       │   │   ├── EscrowStepper.tsx
│       │   │   ├── EvidenceUploader.tsx
│       │   │   └── TradeDetailsPanel.tsx
│       │   └── lib/
│       │       └── wallet.ts       # Freighter browser extension connector
├── indexer/                        # Backend Service: Soroban Event Poller + AI Arbiter
│   ├── src/
│   │   ├── index.ts                # Express REST API server
│   │   ├── eventPoller.ts          # Soroban RPC contract event listener
│   │   ├── aiInvestigator.ts       # Minary moisture shrinkage & split calculator
│   │   └── oracleSigner.ts         # Automated transaction signer for dispute resolution
│   └── test/                       # Invariant and mathematical settlement tests
├── scripts/
│   └── create_issues.sh            # Contributor issue generator
├── pnpm-workspace.yaml
├── package.json
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

---

## Service Topology

```mermaid
flowchart TD
    User["Farmer / Commodity Buyer"]
    Web["Next.js 15 Web dApp (apps/web)"]
    SDK["@agriresolve/sdk (packages/sdk)"]
    RPC["Stellar Soroban RPC (Testnet)"]
    Indexer["Indexer & AI Oracle Service (indexer)"]
    DB[("PostgreSQL Database")]
    Contracts["AgriResolve Smart Contracts (Protocol 22/29)"]

    User -->|Interacts with UI| Web
    Web -->|Calls Contract Entrypoints| SDK
    SDK -->|Simulates & Submits Tx| RPC
    RPC -->|Executes Transactions| Contracts
    Contracts -.->|Emits Contract Events| RPC
    Indexer -->|Polls #[contractevent] Emissions| RPC
    Indexer -->|Caches State & Audits| DB
    Web -->|Submits Weighbridge Receipts & Evidence| Indexer
    Indexer -->|Signs resolve_dispute via Oracle| RPC
```

---

## Design Principles & UI/UX Guardrails

- **Utilitarian Flat Aesthetics**: Strict anti-vibe-coding palette using pure white cards (`bg-white`), crisp 1px borders (`border-[#D1D9D1]`), warm backgrounds (`bg-[#FAF9F5]` landing, `bg-[#F4F7F4]` dashboard), and deep forest green primary accents (`#1E4D2B`). Zero rainbow gradients, zero glassmorphism, zero floating drop shadows.
- **Farmer-First Terminology**: Landing copy contains zero confusing Web3 jargon. Focuses on physical trade delivery protection, verified weight tickets, and objective moisture deductions.
- **Automated AI Oracle Arbitration**: No public arbiter sign-up box. Complex disputes are audited deterministically using regional grain exchange standards (Minary shrinkage formula) and settled atomically on-chain.

---

## Quick Start

### Prerequisites
- Node.js >= 20.0.0
- pnpm >= 9.0.0

### 1. Install Monorepo Dependencies
```bash
pnpm install
```

### 2. Build All Packages & Applications
```bash
# Build SDK, Web app, and Indexer service
pnpm build
```

### 3. Run Automated Unit Test Suites
```bash
# Runs SDK XDR serialization and Indexer mathematical invariant tests
pnpm test
```

### 4. Start Local Development Services
```bash
# Start Next.js web application (http://localhost:3000)
pnpm dev:web

# Start Indexer & AI Arbiter service (http://localhost:8000)
pnpm dev:indexer
```

---

## Environment Configuration

Copy the example environment files into active local configurations:
```bash
# Frontend environment variables
cp apps/web/.env.example apps/web/.env.local

# Indexer backend environment variables
cp indexer/.env.example indexer/.env
```

---

## Maintainers

| Name | Role | GitHub | Telegram | Email |
|---|---|---|---|---|
| **Hassan Korey** | Protocol Architect & Lead Developer | [@HassanKorey](https://github.com/HassanKorey) | [@HassanKorey](https://t.me/HassanKorey) | `edunhassan1006@gmail.com` |

---

## Contributors

Thanks goes to these wonderful people:

<a href="https://github.com/AgriResolve/agriresolve-app/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AgriResolve/agriresolve-app" alt="Contributors" />
</a>

---

## License

This repository is licensed under the [MIT License](LICENSE).
