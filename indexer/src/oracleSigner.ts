import { Keypair } from "@stellar/stellar-sdk";
import { DisputeClient, TESTNET_CONFIG } from "@agriresolve/sdk";

export class OracleSigner {
  private arbiterKeypair: Keypair | null = null;
  private disputeClient: DisputeClient;

  constructor(secretKey?: string, disputeContractId?: string) {
    const key = secretKey || process.env.AI_ARBITER_SECRET_KEY;
    if (key && key.startsWith("S") && key.length === 56) {
      try {
        this.arbiterKeypair = Keypair.fromSecret(key);
        console.log(`[OracleSigner] Loaded AI Arbiter Key: ${this.arbiterKeypair.publicKey()}`);
      } catch (err) {
        console.warn("[OracleSigner] Invalid secret key format, dry-run mode enabled");
      }
    } else {
      console.warn("[OracleSigner] No AI_ARBITER_SECRET_KEY configured; running in simulation/dry-run mode");
    }

    this.disputeClient = new DisputeClient({
      disputeContractId: disputeContractId || process.env.NEXT_PUBLIC_DISPUTE_CONTRACT_ID || TESTNET_CONFIG.disputeContractId,
    });
  }

  public getPublicKey(): string | null {
    return this.arbiterKeypair ? this.arbiterKeypair.publicKey() : null;
  }

  /**
   * Automatically signs and submits the resolution transaction to agriresolve-dispute
   */
  public async submitResolution(
    disputeId: bigint | number,
    buyerShare: bigint | number,
    farmerShare: bigint | number,
    resolutionHash: string | Buffer
  ): Promise<{ txHash: string; status: "submitted" | "dry-run" }> {
    if (!this.arbiterKeypair) {
      console.log(`[OracleSigner] DRY-RUN: resolve_dispute(${disputeId}, buyer=${buyerShare}, farmer=${farmerShare})`);
      return {
        txHash: `sim_${Date.now()}_dry_run_resolution`,
        status: "dry-run",
      };
    }

    try {
      console.log(`[OracleSigner] Submitting resolve_dispute for dispute #${disputeId}...`);
      const txHash = await this.disputeClient.resolveDispute(
        this.arbiterKeypair,
        disputeId,
        buyerShare,
        farmerShare,
        resolutionHash
      );
      console.log(`[OracleSigner] Transaction confirmed on Stellar Testnet: ${txHash}`);
      return { txHash, status: "submitted" };
    } catch (error: any) {
      console.error(`[OracleSigner] Error submitting resolution on-chain:`, error);
      throw error;
    }
  }
}
