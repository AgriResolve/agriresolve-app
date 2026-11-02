import assert from "node:assert";
import test from "node:test";
import { AIDisputeInvestigator, InspectionData, TradeTerms } from "../src/aiInvestigator";

test("AIDisputeInvestigator - Minary shrinkage calculation", () => {
  // Case 1: Produce meets or is drier than base moisture (no shrinkage)
  const exact = AIDisputeInvestigator.calculateMinaryShrinkage(10000, 1200, 1200);
  assert.strictEqual(exact.adjustedKg, 10000);
  assert.strictEqual(exact.shrinkageLossKg, 0);

  // Case 2: Produce has excess moisture (16.00% vs 12.00% base)
  // Dry matter factor = (10000 - 1600) / (10000 - 1200) = 8400 / 8800 = ~0.954545
  const wet = AIDisputeInvestigator.calculateMinaryShrinkage(10000, 1600, 1200);
  assert.strictEqual(wet.adjustedKg, 9545.45);
  assert.strictEqual(wet.shrinkageLossKg, 454.55);
});

test("AIDisputeInvestigator - Invariant Conservation: farmer_share + buyer_share == tradeAmount", () => {
  const investigator = new AIDisputeInvestigator();

  const scenarios: { terms: TradeTerms; inspection: InspectionData }[] = [
    {
      // Perfect delivery
      terms: {
        escrowId: 1n,
        totalAmount: 10000000000n, // $1,000.00
        contractQuantityKg: 10000,
        contractPricePerKg: 0.1,
        baseMoistureBps: 1200,
        maxMoistureBps: 1450,
        deliveryToleranceBps: 500,
        shrinkageFactorBps: 125,
      },
      inspection: {
        deliveredQuantityKg: 10000,
        actualMoistureBps: 1200,
      },
    },
    {
      // Wet delivery with moisture shrinkage
      terms: {
        escrowId: 2n,
        totalAmount: 50000000000n, // $5,000.00
        contractQuantityKg: 25000,
        contractPricePerKg: 0.2,
        baseMoistureBps: 1250,
        maxMoistureBps: 1400,
        deliveryToleranceBps: 300,
        shrinkageFactorBps: 125,
      },
      inspection: {
        deliveredQuantityKg: 25000,
        actualMoistureBps: 1550, // 300 bps excess
      },
    },
    {
      // Severe delivery shortfall + high moisture
      terms: {
        escrowId: 3n,
        totalAmount: 123456789012n,
        contractQuantityKg: 50000,
        contractPricePerKg: 0.2469,
        baseMoistureBps: 1200,
        maxMoistureBps: 1450,
        deliveryToleranceBps: 500,
        shrinkageFactorBps: 125,
      },
      inspection: {
        deliveredQuantityKg: 35000, // 15,000 kg shortfall
        actualMoistureBps: 1650,
      },
    },
  ];

  for (const scenario of scenarios) {
    const report = investigator.evaluateDispute(scenario.terms, scenario.inspection);

    // Invariant 1: Bps split sum is strictly 10,000
    assert.strictEqual(report.buyerBps + report.farmerBps, 10000);

    // Invariant 2: Mathematical conservation of balance
    assert.strictEqual(
      report.buyerShare + report.farmerShare,
      scenario.terms.totalAmount,
      `Conservation failed for escrow #${scenario.terms.escrowId}`
    );

    // Invariant 3: Valid 32-byte sha256 resolution hash
    assert.strictEqual(report.resolutionHash.length, 64);
  }
});
