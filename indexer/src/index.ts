import express, { Request, Response } from "express";
import cors from "cors";
import dotenv from "dotenv";
import { AIDisputeInvestigator, InvestigationEvidence, InspectionData, TradeTerms } from "./aiInvestigator";
import { OracleSigner } from "./oracleSigner";
import { SorobanEventPoller } from "./eventPoller";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8000;
const investigator = new AIDisputeInvestigator();
const oracleSigner = new OracleSigner();
const eventPoller = new SorobanEventPoller();

// In-memory reports cache
const reportCache = new Map<string, any>();

// Healthcheck
app.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "ok",
    service: "AgriResolve-Indexer & AI Oracle",
    timestamp: new Date().toISOString(),
    arbiterAddress: oracleSigner.getPublicKey() || "dry-run-mode",
  });
});

/**
 * POST /api/disputes/:escrowId/investigate
 * Ingests trade agreements, delivery weighbridge receipts, and inspection logs,
 * calculates deterministic settlement shares (farmer_bps + buyer_bps === 10000),
 * generates SHA-256 report digest, and submits on-chain resolution.
 */
app.post("/api/disputes/:escrowId/investigate", async (req: Request, res: Response): Promise<void> => {
  try {
    const escrowId = req.params.escrowId;
    const { terms, inspection, evidenceList, disputeId, autoSubmitOnChain } = req.body;

    if (!terms || !inspection) {
      res.status(400).json({ error: "Missing required payload: terms and inspection are mandatory." });
      return;
    }

    const tradeTerms: TradeTerms = {
      escrowId,
      totalAmount: BigInt(terms.totalAmount || "0"),
      contractQuantityKg: Number(terms.contractQuantityKg || 10000),
      contractPricePerKg: Number(terms.contractPricePerKg || 1),
      baseMoistureBps: Number(terms.baseMoistureBps || 1200),
      maxMoistureBps: Number(terms.maxMoistureBps || 1450),
      deliveryToleranceBps: Number(terms.deliveryToleranceBps || 500),
      shrinkageFactorBps: Number(terms.shrinkageFactorBps || 125),
    };

    const inspectionData: InspectionData = {
      deliveredQuantityKg: Number(inspection.deliveredQuantityKg || 10000),
      actualMoistureBps: Number(inspection.actualMoistureBps || 1200),
      foreignMatterBps: Number(inspection.foreignMatterBps || 0),
      brokenGrainBps: Number(inspection.brokenGrainBps || 0),
      weighbridgeTicketId: inspection.weighbridgeTicketId,
      inspectorAddress: inspection.inspectorAddress,
    };

    const evidence: InvestigationEvidence[] = Array.isArray(evidenceList) ? evidenceList : [];

    // Run deterministic investigation
    const report = investigator.evaluateDispute(tradeTerms, inspectionData, evidence);

    let onChainResult: { txHash: string; status: string } | null = null;
    if (autoSubmitOnChain && disputeId) {
      onChainResult = await oracleSigner.submitResolution(
        BigInt(disputeId),
        report.buyerShare,
        report.farmerShare,
        report.resolutionHash
      );
    }

    const responsePayload = {
      report: {
        ...report,
        escrowId: report.escrowId.toString(),
        tradeAmount: report.tradeAmount.toString(),
        buyerShare: report.buyerShare.toString(),
        farmerShare: report.farmerShare.toString(),
      },
      onChainResult,
    };

    reportCache.set(escrowId, responsePayload);

    res.json(responsePayload);
  } catch (error: any) {
    console.error("[API] Investigation error:", error);
    res.status(500).json({ error: error.message || "Failed to process dispute investigation" });
  }
});

/**
 * GET /api/disputes/:escrowId/report
 */
app.get("/api/disputes/:escrowId/report", (req: Request, res: Response): void => {
  const escrowId = req.params.escrowId;
  const cached = reportCache.get(escrowId);
  if (!cached) {
    res.status(404).json({ error: `No investigation report found for escrow #${escrowId}` });
    return;
  }
  res.json(cached);
});

// Start server
if (process.env.NODE_ENV !== "test") {
  app.listen(PORT, () => {
    console.log(`==========================================================`);
    console.log(`  AgriResolve Indexer & AI Arbiter Service online`);
    console.log(`  Listening on port ${PORT}`);
    console.log(`==========================================================`);

    // Start background event poller
    eventPoller.start().catch((err) => console.error("[EventPoller] Startup error:", err));
  });
}

export { app, investigator, oracleSigner, eventPoller };
