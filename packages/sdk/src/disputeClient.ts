import {
  Address,
  Contract,
  Keypair,
  nativeToScVal,
  rpc,
  scValToNative,
  TransactionBuilder,
  xdr,
} from "@stellar/stellar-sdk";
import { DisputeRecord, DisputeStatus, EvidenceRecord, NetworkConfig, TESTNET_CONFIG } from "./types";
import {
  addressToScVal,
  bytes32ToScVal,
  i128ToScVal,
  symbolToScVal,
  u32ToScVal,
  u64ToScVal,
} from "./xdr";

export class DisputeClient {
  public readonly server: rpc.Server;
  public readonly contract: Contract;
  public readonly config: NetworkConfig;

  constructor(config: Partial<NetworkConfig> = {}) {
    this.config = { ...TESTNET_CONFIG, ...config };
    this.server = new rpc.Server(this.config.rpcUrl);
    this.contract = new Contract(this.config.disputeContractId);
  }

  private async readCall(method: string, args: xdr.ScVal[] = []): Promise<xdr.ScVal | null> {
    const account = new rpc.Account(
      "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWHF",
      "0"
    );
    const tx = new TransactionBuilder(account, {
      fee: "100",
      networkPassphrase: this.config.networkPassphrase,
    })
      .addOperation(this.contract.call(method, ...args))
      .setTimeout(30)
      .build();

    const sim = await this.server.simulateTransaction(tx);
    if (rpc.Api.isSimulationError(sim)) {
      throw new Error(`Simulation error invoking ${method}: ${sim.error}`);
    }
    if (sim.result) {
      return sim.result.retval;
    }
    return null;
  }

  public async writeCall(
    signer: Keypair,
    method: string,
    args: xdr.ScVal[]
  ): Promise<string> {
    const sourceAccount = await this.server.getAccount(signer.publicKey());
    const baseTx = new TransactionBuilder(sourceAccount, {
      fee: "10000",
      networkPassphrase: this.config.networkPassphrase,
    })
      .addOperation(this.contract.call(method, ...args))
      .setTimeout(60)
      .build();

    const prepared = await this.server.prepareTransaction(baseTx);
    prepared.sign(signer);

    const sendRes = await this.server.sendTransaction(prepared);
    if (sendRes.status === "ERROR") {
      throw new Error(`Transaction submission error: ${JSON.stringify(sendRes)}`);
    }

    let status = sendRes.status;
    let pollCount = 0;
    while (status === "PENDING" && pollCount < 30) {
      await new Promise((r) => setTimeout(r, 1000));
      const txRes = await this.server.getTransaction(sendRes.hash);
      status = txRes.status;
      if (status === "SUCCESS") {
        return sendRes.hash;
      } else if (status === "FAILED") {
        throw new Error(`Transaction failed on ledger: ${sendRes.hash}`);
      }
      pollCount++;
    }

    return sendRes.hash;
  }

  public async getDisputeCount(): Promise<bigint> {
    const retval = await this.readCall("get_dispute_count");
    if (!retval) return 0n;
    return BigInt(scValToNative(retval) || 0);
  }

  public async getEscrowContract(): Promise<string | null> {
    const retval = await this.readCall("get_escrow_contract");
    if (!retval) return null;
    const native = scValToNative(retval);
    return native ? String(native) : null;
  }

  public async getDisputeByEscrow(escrowId: bigint | number): Promise<bigint | null> {
    const retval = await this.readCall("get_dispute_by_escrow", [u64ToScVal(escrowId)]);
    if (!retval) return null;
    const native = scValToNative(retval);
    return native !== null && native !== undefined ? BigInt(native) : null;
  }

  public async getDispute(disputeId: bigint | number): Promise<DisputeRecord | null> {
    const retval = await this.readCall("get_dispute", [u64ToScVal(disputeId)]);
    if (!retval) return null;
    const raw = scValToNative(retval);
    if (!raw) return null;

    let complaintHex = "";
    if (raw.complaint_hash) {
      complaintHex = Buffer.isBuffer(raw.complaint_hash)
        ? raw.complaint_hash.toString("hex")
        : String(raw.complaint_hash);
    }

    return {
      disputeId: BigInt(raw.dispute_id),
      escrowId: BigInt(raw.escrow_id),
      claimant: String(raw.claimant),
      defendant: String(raw.defendant),
      arbiter: String(raw.arbiter),
      complaintHash: complaintHex,
      status: Number(raw.status) as DisputeStatus,
      buyerShare: BigInt(raw.buyer_share),
      farmerShare: BigInt(raw.farmer_share),
      evidenceCount: Number(raw.evidence_count),
    };
  }

  public async getEvidence(
    disputeId: bigint | number,
    evidenceIndex: number
  ): Promise<EvidenceRecord | null> {
    const retval = await this.readCall("get_evidence", [
      u64ToScVal(disputeId),
      u32ToScVal(evidenceIndex),
    ]);
    if (!retval) return null;
    const raw = scValToNative(retval);
    if (!raw) return null;

    let hashHex = "";
    if (raw.evidence_hash) {
      hashHex = Buffer.isBuffer(raw.evidence_hash)
        ? raw.evidence_hash.toString("hex")
        : String(raw.evidence_hash);
    }

    return {
      evidenceIndex: Number(raw.evidence_index),
      submitter: String(raw.submitter),
      evidenceType: String(raw.evidence_type),
      evidenceHash: hashHex,
      submittedAt: BigInt(raw.submitted_at || 0),
    };
  }

  public async raiseDispute(
    claimant: Keypair,
    escrowId: bigint | number,
    complaintHash: string | Buffer
  ): Promise<string> {
    return this.writeCall(claimant, "raise_dispute", [
      addressToScVal(claimant.publicKey()),
      u64ToScVal(escrowId),
      bytes32ToScVal(complaintHash),
    ]);
  }

  public async submitEvidence(
    submitter: Keypair,
    disputeId: bigint | number,
    evidenceType: string,
    evidenceHash: string | Buffer
  ): Promise<string> {
    return this.writeCall(submitter, "submit_evidence", [
      addressToScVal(submitter.publicKey()),
      u64ToScVal(disputeId),
      symbolToScVal(evidenceType),
      bytes32ToScVal(evidenceHash),
    ]);
  }

  public async resolveDispute(
    arbiter: Keypair,
    disputeId: bigint | number,
    buyerShare: bigint | number,
    farmerShare: bigint | number,
    resolutionHash: string | Buffer
  ): Promise<string> {
    return this.writeCall(arbiter, "resolve_dispute", [
      addressToScVal(arbiter.publicKey()),
      u64ToScVal(disputeId),
      i128ToScVal(buyerShare),
      i128ToScVal(farmerShare),
      bytes32ToScVal(resolutionHash),
    ]);
  }

  public async dismissDispute(
    arbiter: Keypair,
    disputeId: bigint | number
  ): Promise<string> {
    return this.writeCall(arbiter, "dismiss_dispute", [
      addressToScVal(arbiter.publicKey()),
      u64ToScVal(disputeId),
    ]);
  }
}
