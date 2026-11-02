import assert from "node:assert";
import test from "node:test";
import {
  addressToScVal,
  boolToScVal,
  bytes32ToScVal,
  DisputeClient,
  EscrowClient,
  i128ToScVal,
  RegistryClient,
  scValToNative,
  sha256Digest,
  stringToScVal,
  symbolToScVal,
  TESTNET_CONFIG,
  u32ToScVal,
  u64ToScVal,
} from "../src";

test("SDK XDR Helpers - basic value conversions", () => {
  const boolVal = boolToScVal(true);
  assert.strictEqual(scValToNative(boolVal), true);

  const u32Val = u32ToScVal(1200);
  assert.strictEqual(Number(scValToNative(u32Val)), 1200);

  const u64Val = u64ToScVal(1000000000n);
  assert.strictEqual(BigInt(scValToNative(u64Val)), 1000000000n);

  const i128Val = i128ToScVal(50000000000n);
  assert.strictEqual(BigInt(scValToNative(i128Val)), 50000000000n);

  const symVal = symbolToScVal("MAIZE");
  assert.strictEqual(scValToNative(symVal), "MAIZE");

  const strVal = stringToScVal("ipfs://bafybeic7...");
  assert.strictEqual(scValToNative(strVal), "ipfs://bafybeic7...");
});

test("SDK XDR Helpers - bytes32 and sha256 hashing", () => {
  const sampleData = "Weighbridge Delivery Ticket #9812";
  const digest = sha256Digest(sampleData);
  assert.strictEqual(digest.length, 32);

  const scVal = bytes32ToScVal(digest);
  const back = scValToNative(scVal);
  assert.strictEqual(Buffer.from(back).toString("hex"), digest.toString("hex"));
});

test("SDK XDR Helpers - Stellar Address encoding", () => {
  const testAddress = "GCBOKYT7TAARXDILFZ43QX2WWIRHAWA2S3V3ZP7EWN4KWTDIBS3NQS4Y";
  const scVal = addressToScVal(testAddress);
  const decoded = scValToNative(scVal);
  assert.strictEqual(decoded, testAddress);
});

test("SDK Client Configurations & Live Contract IDs", () => {
  assert.strictEqual(TESTNET_CONFIG.registryContractId.startsWith("C"), true);
  assert.strictEqual(TESTNET_CONFIG.registryContractId.length, 56);
  assert.strictEqual(TESTNET_CONFIG.escrowContractId.startsWith("C"), true);
  assert.strictEqual(TESTNET_CONFIG.escrowContractId.length, 56);
  assert.strictEqual(TESTNET_CONFIG.disputeContractId.startsWith("C"), true);
  assert.strictEqual(TESTNET_CONFIG.disputeContractId.length, 56);

  const regClient = new RegistryClient();
  assert.strictEqual(regClient.contract.contractId(), TESTNET_CONFIG.registryContractId);

  const escrowClient = new EscrowClient();
  assert.strictEqual(escrowClient.contract.contractId(), TESTNET_CONFIG.escrowContractId);

  const disputeClient = new DisputeClient();
  assert.strictEqual(disputeClient.contract.contractId(), TESTNET_CONFIG.disputeContractId);
});
