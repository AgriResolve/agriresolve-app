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
import {
  CommoditySpec,
  NetworkConfig,
  ParticipantProfile,
  ParticipantRole,
  TESTNET_CONFIG,
} from "./types";
import {
  addressToScVal,
  boolToScVal,
  stringToScVal,
  symbolToScVal,
  u32ToScVal,
} from "./xdr";

export class RegistryClient {
  public readonly server: rpc.Server;
  public readonly contract: Contract;
  public readonly config: NetworkConfig;

  constructor(config: Partial<NetworkConfig> = {}) {
    this.config = { ...TESTNET_CONFIG, ...config };
    this.server = new rpc.Server(this.config.rpcUrl);
    this.contract = new Contract(this.config.registryContractId);
  }

  /**
   * Helper to perform read-only simulation
   */
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

  /**
   * Helper to perform signed write transaction
   */
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

  // Contract Methods

  public async getAdmin(): Promise<string | null> {
    const retval = await this.readCall("get_admin");
    if (!retval) return null;
    const native = scValToNative(retval);
    return native ? String(native) : null;
  }

  public async getParticipantCount(): Promise<number> {
    const retval = await this.readCall("get_participant_count");
    if (!retval) return 0;
    return Number(scValToNative(retval) || 0);
  }

  public async isTokenApproved(token: string): Promise<boolean> {
    const retval = await this.readCall("is_token_approved", [addressToScVal(token)]);
    if (!retval) return false;
    return Boolean(scValToNative(retval));
  }

  public async isParticipantActive(participant: string): Promise<boolean> {
    const retval = await this.readCall("is_participant_active", [addressToScVal(participant)]);
    if (!retval) return false;
    return Boolean(scValToNative(retval));
  }

  public async isParticipantRole(participant: string, role: ParticipantRole): Promise<boolean> {
    const retval = await this.readCall("is_participant_role", [
      addressToScVal(participant),
      u32ToScVal(role),
    ]);
    if (!retval) return false;
    return Boolean(scValToNative(retval));
  }

  public async getParticipant(participant: string): Promise<ParticipantProfile | null> {
    const retval = await this.readCall("get_participant", [addressToScVal(participant)]);
    if (!retval) return null;
    const raw = scValToNative(retval);
    if (!raw) return null;
    return {
      role: Number(raw.role) as ParticipantRole,
      metadataUri: String(raw.metadata_uri || ""),
      isActive: Boolean(raw.is_active),
      registeredAt: BigInt(raw.registered_at || 0),
    };
  }

  public async getCommodity(commodityId: string): Promise<CommoditySpec | null> {
    const retval = await this.readCall("get_commodity", [symbolToScVal(commodityId)]);
    if (!retval) return null;
    const raw = scValToNative(retval);
    if (!raw) return null;
    return {
      baseMoistureBps: Number(raw.base_moisture_bps),
      maxMoistureBps: Number(raw.max_moisture_bps),
      deliveryToleranceBps: Number(raw.delivery_tolerance_bps),
      shrinkageFactorBps: Number(raw.shrinkage_factor_bps),
    };
  }

  public async registerParticipant(
    admin: Keypair,
    participant: string,
    role: ParticipantRole,
    metadataUri: string
  ): Promise<string> {
    return this.writeCall(admin, "register_participant", [
      addressToScVal(admin.publicKey()),
      addressToScVal(participant),
      u32ToScVal(role),
      stringToScVal(metadataUri),
    ]);
  }

  public async updateParticipantStatus(
    admin: Keypair,
    participant: string,
    isActive: boolean
  ): Promise<string> {
    return this.writeCall(admin, "update_participant_status", [
      addressToScVal(admin.publicKey()),
      addressToScVal(participant),
      boolToScVal(isActive),
    ]);
  }

  public async registerCommodity(
    admin: Keypair,
    commodityId: string,
    spec: CommoditySpec
  ): Promise<string> {
    const specScVal = nativeToScVal(
      {
        base_moisture_bps: spec.baseMoistureBps,
        max_moisture_bps: spec.maxMoistureBps,
        delivery_tolerance_bps: spec.deliveryToleranceBps,
        shrinkage_factor_bps: spec.shrinkageFactorBps,
      },
      {
        type: {
          base_moisture_bps: ["u32"],
          max_moisture_bps: ["u32"],
          delivery_tolerance_bps: ["u32"],
          shrinkage_factor_bps: ["u32"],
        },
      }
    );

    return this.writeCall(admin, "register_commodity", [
      addressToScVal(admin.publicKey()),
      symbolToScVal(commodityId),
      specScVal,
    ]);
  }

  public async setTokenWhitelist(
    admin: Keypair,
    token: string,
    isApproved: boolean
  ): Promise<string> {
    return this.writeCall(admin, "set_token_whitelist", [
      addressToScVal(admin.publicKey()),
      addressToScVal(token),
      boolToScVal(isApproved),
    ]);
  }
}
