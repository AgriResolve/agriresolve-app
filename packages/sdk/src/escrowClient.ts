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
import { EscrowState, NetworkConfig, TESTNET_CONFIG, TradeDetails } from "./types";
import {
  addressToScVal,
  bytes32ToScVal,
  i128ToScVal,
  u64ToScVal,
} from "./xdr";

export class EscrowClient {
  public readonly server: rpc.Server;
  public readonly contract: Contract;
  public readonly config: NetworkConfig;

  constructor(config: Partial<NetworkConfig> = {}) {
    this.config = { ...TESTNET_CONFIG, ...config };
    this.server = new rpc.Server(this.config.rpcUrl);
    this.contract = new Contract(this.config.escrowContractId);
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

  public async getTradeCount(): Promise<bigint> {
    const retval = await this.readCall("get_trade_count");
    if (!retval) return 0n;
    return BigInt(scValToNative(retval) || 0);
  }

  public async getDisputeContract(): Promise<string | null> {
    const retval = await this.readCall("get_dispute_contract");
    if (!retval) return null;
    const native = scValToNative(retval);
    return native ? String(native) : null;
  }

  public async getTrade(tradeId: bigint | number): Promise<TradeDetails | null> {
    const retval = await this.readCall("get_trade", [u64ToScVal(tradeId)]);
    if (!retval) return null;
    const raw = scValToNative(retval);
    if (!raw) return null;

    let deliveryHex = "";
    if (raw.delivery_hash) {
      deliveryHex = Buffer.isBuffer(raw.delivery_hash)
        ? raw.delivery_hash.toString("hex")
        : String(raw.delivery_hash);
    }

    return {
      tradeId: BigInt(raw.trade_id),
      buyer: String(raw.buyer),
      farmer: String(raw.farmer),
      arbiter: String(raw.arbiter),
      token: String(raw.token),
      amount: BigInt(raw.amount),
      expiry: BigInt(raw.expiry),
      state: Number(raw.state) as EscrowState,
      deliveryHash: deliveryHex,
    };
  }

  public async initializeTrade(
    buyer: Keypair,
    farmer: string,
    arbiter: string,
    token: string,
    amount: bigint | number,
    expiry: bigint | number
  ): Promise<string> {
    return this.writeCall(buyer, "initialize_trade", [
      addressToScVal(buyer.publicKey()),
      addressToScVal(farmer),
      addressToScVal(arbiter),
      addressToScVal(token),
      i128ToScVal(amount),
      u64ToScVal(expiry),
    ]);
  }

  public async confirmDelivery(
    farmer: Keypair,
    tradeId: bigint | number,
    deliveryHash: string | Buffer
  ): Promise<string> {
    return this.writeCall(farmer, "confirm_delivery", [
      addressToScVal(farmer.publicKey()),
      u64ToScVal(tradeId),
      bytes32ToScVal(deliveryHash),
    ]);
  }

  public async flagDispute(caller: Keypair, tradeId: bigint | number): Promise<string> {
    return this.writeCall(caller, "flag_dispute", [
      addressToScVal(caller.publicKey()),
      u64ToScVal(tradeId),
    ]);
  }

  public async executeResolution(
    caller: Keypair,
    tradeId: bigint | number,
    buyerShare: bigint | number,
    farmerShare: bigint | number
  ): Promise<string> {
    return this.writeCall(caller, "execute_resolution", [
      addressToScVal(caller.publicKey()),
      u64ToScVal(tradeId),
      i128ToScVal(buyerShare),
      i128ToScVal(farmerShare),
    ]);
  }

  public async refundTrade(caller: Keypair, tradeId: bigint | number): Promise<string> {
    return this.writeCall(caller, "refund_trade", [
      addressToScVal(caller.publicKey()),
      u64ToScVal(tradeId),
    ]);
  }

  public async setDisputeContract(
    admin: Keypair,
    disputeContract: string
  ): Promise<string> {
    return this.writeCall(admin, "set_dispute_contract", [
      addressToScVal(admin.publicKey()),
      addressToScVal(disputeContract),
    ]);
  }
}
