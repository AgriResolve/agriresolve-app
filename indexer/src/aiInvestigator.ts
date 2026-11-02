import { createHash } from "node:crypto";

export interface InvestigationEvidence {
  evidenceType: string;
  sourceUri: string;
  hash: string;
  contentSummary: string;
}

export interface TradeTerms {
  escrowId: bigint | number;
  totalAmount: bigint;
  contractQuantityKg: number;
  contractPricePerKg: number;
  baseMoistureBps: number;       // e.g. 1200 = 12.00%
  maxMoistureBps: number;        // e.g. 1450 = 14.50%
  deliveryToleranceBps: number;  // e.g. 500 = 5.00%
  shrinkageFactorBps: number;    // e.g. 125 = 1.25%
}

export interface InspectionData {
  deliveredQuantityKg: number;
  actualMoistureBps: number;     // e.g. 1520 = 15.20%
  foreignMatterBps?: number;     // e.g. 150 = 1.50%
  brokenGrainBps?: number;       // e.g. 200 = 2.00%
  weighbridgeTicketId?: string;
  inspectorAddress?: string;
}

export interface InvestigationReport {
  escrowId: bigint;
  tradeAmount: bigint;
  buyerShare: bigint;
  farmerShare: bigint;
  buyerBps: number;
  farmerBps: number;
  deliveredQuantityKg: number;
  adjustedQuantityKg: number;
  shrinkageLossKg: number;
  isWithinTolerance: boolean;
  findings: string[];
  evidenceAudit: InvestigationEvidence[];
  resolutionHash: string;
  timestamp: number;
}

export class AIDisputeInvestigator {
  /**
   * Deterministic Minary formula for moisture shrinkage
   * Adjusted Weight = Delivered * ((10,000 - Actual Moisture Bps) / (10,000 - Base Moisture Bps))
   */
  public static calculateMinaryShrinkage(
    deliveredKg: number,
    actualMoistureBps: number,
    baseMoistureBps: number
  ): { adjustedKg: number; shrinkageLossKg: number } {
    if (actualMoistureBps <= baseMoistureBps) {
      return { adjustedKg: deliveredKg, shrinkageLossKg: 0 };
    }

    const dryMatterDelivered = 10000 - actualMoistureBps;
    const dryMatterBase = 10000 - baseMoistureBps;

    const dryMatterFactor = dryMatterDelivered / dryMatterBase;
    const adjustedKg = Math.max(0, deliveredKg * dryMatterFactor);
    const shrinkageLossKg = deliveredKg - adjustedKg;

    return {
      adjustedKg: Math.round(adjustedKg * 100) / 100,
      shrinkageLossKg: Math.round(shrinkageLossKg * 100) / 100,
    };
  }

  /**
   * Evaluates trade terms, delivery weighbridge receipts, and lab moisture sensor logs
   * Returns deterministic buyer_share and farmer_share where buyer_share + farmer_share == tradeAmount
   */
  public evaluateDispute(
    terms: TradeTerms,
    inspection: InspectionData,
    evidenceList: InvestigationEvidence[] = []
  ): InvestigationReport {
    const findings: string[] = [];
    const totalAmount = BigInt(terms.totalAmount);
    const contractKg = terms.contractQuantityKg;
    const deliveredKg = inspection.deliveredQuantityKg;

    // 1. Quantity Variance & Tolerance Check
    const quantityVarianceKg = deliveredKg - contractKg;
    const allowedShortfallKg = contractKg * (terms.deliveryToleranceBps / 10000);
    const isWithinTolerance = Math.abs(quantityVarianceKg) <= allowedShortfallKg;

    findings.push(
      `Delivered ${deliveredKg} kg against contracted ${contractKg} kg (Variance: ${quantityVarianceKg.toFixed(2)} kg).`
    );

    if (!isWithinTolerance && quantityVarianceKg < 0) {
      findings.push(
        `Delivery shortfall exceeds allowable contractual tolerance of ${(terms.deliveryToleranceBps / 100).toFixed(2)}%.`
      );
    } else {
      findings.push(
        `Weight variance is within allowable contractual tolerance of ${(terms.deliveryToleranceBps / 100).toFixed(2)}%.`
      );
    }

    // 2. Moisture Shrinkage Calculation
    const { adjustedKg, shrinkageLossKg } = AIDisputeInvestigator.calculateMinaryShrinkage(
      deliveredKg,
      inspection.actualMoistureBps,
      terms.baseMoistureBps
    );

    let moisturePenaltyBps = 0;
    if (inspection.actualMoistureBps > terms.baseMoistureBps) {
      const excessMoistureBps = inspection.actualMoistureBps - terms.baseMoistureBps;
      moisturePenaltyBps = Math.min(
        10000,
        Math.round((shrinkageLossKg / deliveredKg) * 10000)
      );

      findings.push(
        `Actual moisture ${(inspection.actualMoistureBps / 100).toFixed(2)}% exceeded standard base moisture ${(terms.baseMoistureBps / 100).toFixed(2)}%. Minary shrinkage loss: ${shrinkageLossKg.toFixed(2)} kg (${(moisturePenaltyBps / 100).toFixed(2)}% deduction).`
      );
    } else {
      findings.push(
        `Produce met or surpassed baseline moisture specification: ${(inspection.actualMoistureBps / 100).toFixed(2)}% <= ${(terms.baseMoistureBps / 100).toFixed(2)}%.`
      );
    }

    // 3. Shortfall Penalty
    let shortfallPenaltyBps = 0;
    if (quantityVarianceKg < 0 && !isWithinTolerance) {
      const netShortfallKg = Math.abs(quantityVarianceKg) - allowedShortfallKg;
      shortfallPenaltyBps = Math.min(
        10000,
        Math.round((netShortfallKg / contractKg) * 10000)
      );
      findings.push(
        `Shortfall penalty applied: ${(shortfallPenaltyBps / 100).toFixed(2)}% compensation for missing grain.`
      );
    }

    // 4. Calculate Final Split (Total Bps = 10,000)
    let buyerBps = moisturePenaltyBps + shortfallPenaltyBps;
    if (buyerBps > 10000) buyerBps = 10000;
    if (buyerBps < 0) buyerBps = 0;

    const farmerBps = 10000 - buyerBps;

    // Strict invariant: buyer_share + farmer_share == totalAmount
    const buyerShare = (totalAmount * BigInt(buyerBps)) / 10000n;
    const farmerShare = totalAmount - buyerShare;

    findings.push(
      `Final partition: Buyer refund ${buyerShare.toString()} units (${(buyerBps / 100).toFixed(2)}%), Farmer disbursement ${farmerShare.toString()} units (${(farmerBps / 100).toFixed(2)}%).`
    );

    // 5. Compute Deterministic 32-byte Resolution Hash
    const rawReportPayload = JSON.stringify({
      escrowId: terms.escrowId.toString(),
      totalAmount: totalAmount.toString(),
      buyerShare: buyerShare.toString(),
      farmerShare: farmerShare.toString(),
      buyerBps,
      farmerBps,
      findings,
      evidenceHashes: evidenceList.map((e) => e.hash),
    });

    const resolutionHash = createHash("sha256").update(rawReportPayload).digest("hex");

    return {
      escrowId: BigInt(terms.escrowId),
      tradeAmount: totalAmount,
      buyerShare,
      farmerShare,
      buyerBps,
      farmerBps,
      deliveredQuantityKg: deliveredKg,
      adjustedQuantityKg: adjustedKg,
      shrinkageLossKg,
      isWithinTolerance,
      findings,
      evidenceAudit: evidenceList,
      resolutionHash,
      timestamp: Math.floor(Date.now() / 1000),
    };
  }
}
