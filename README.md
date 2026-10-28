# AgriResolve: Application Workspace (`agriresolve-app`)

> Full-stack agricultural escrow management dashboard and autonomous AI evidence investigation pipeline.

## Directory Structure

```
agriresolve-app/
├── package.json
├── pnpm-workspace.yaml
├── apps/
│   └── web/                   # Next.js 15 App Router dApp with Freighter wallet connect
│       ├── app/
│       │   ├── layout.tsx     # Theme, navbar, global styles
│       │   ├── page.tsx       # Escrow trades dashboard & metrics
│       │   ├── trade/
│       │   │   ├── new/       # Open new trade form
│       │   │   └── [id]/      # Detailed trade state machine controls & dispute resolution
│       │   ├── disputes/      # AI evidence audit interface
│       │   └── api/           # API routes bridging AI pipeline
│       └── components/        # WalletConnect, TradeCard, EvidenceUploader, ResolutionModal
└── services/
    └── ai_agent/              # Off-chain evidence parsing & proof generator pipeline
        ├── agriresolve/       # Meterless World Model, Nemotron investigator, and tools
        ├── proof_bridge.py    # DisputeResolutionProof and contract params formatter
        ├── server.py          # REST server for off-chain evidence audits
        └── demo.py            # CLI test scenarios
```

## Quick Start

### 1. Web Application (`apps/web`)

```bash
cd agriresolve-app/apps/web

# Install dependencies
pnpm install

# Run local development server
pnpm dev

# Build production bundle
pnpm build
```

### 2. AI Evidence Agent (`services/ai_agent`)

```bash
cd agriresolve-app/services/ai_agent

# Install Python requirements
pip install -r requirements.txt

# Run CLI demonstration on dispute scenarios
python3 demo.py --scenario DISP-MAIZE-002-DISPUTE

# Start HTTP evidence audit bridge
python3 server.py
```
