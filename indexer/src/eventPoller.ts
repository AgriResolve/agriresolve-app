import { rpc, scValToNative } from "@stellar/stellar-sdk";
import { TESTNET_CONFIG } from "@agriresolve/sdk";

export interface PolledEvent {
  id: string;
  contractId: string;
  ledger: number;
  ledgerClosedAt: string;
  topic: string[];
  data: any;
}

export class SorobanEventPoller {
  private server: rpc.Server;
  private lastLedger: number = 0;
  private contractIds: string[];
  private isPolling: boolean = false;
  private timer: NodeJS.Timeout | null = null;
  private listeners: ((event: PolledEvent) => void)[] = [];

  constructor(
    rpcUrl: string = process.env.NEXT_PUBLIC_SOROBAN_RPC_URL || TESTNET_CONFIG.rpcUrl,
    contractIds: string[] = [
      process.env.NEXT_PUBLIC_REGISTRY_CONTRACT_ID || TESTNET_CONFIG.registryContractId,
      process.env.NEXT_PUBLIC_ESCROW_CONTRACT_ID || TESTNET_CONFIG.escrowContractId,
      process.env.NEXT_PUBLIC_DISPUTE_CONTRACT_ID || TESTNET_CONFIG.disputeContractId,
    ]
  ) {
    this.server = new rpc.Server(rpcUrl);
    this.contractIds = contractIds.filter(Boolean);
  }

  public onEvent(callback: (event: PolledEvent) => void) {
    this.listeners.push(callback);
  }

  public async start(intervalMs: number = 5000) {
    if (this.isPolling) return;
    this.isPolling = true;

    try {
      const latest = await this.server.getLatestLedger();
      this.lastLedger = Math.max(1, latest.sequence - 100);
      console.log(`[EventPoller] Initialized at ledger sequence ${this.lastLedger}`);
    } catch (err) {
      console.warn(`[EventPoller] Could not query latest ledger, defaulting to 1:`, err);
      this.lastLedger = 1;
    }

    this.timer = setInterval(() => this.poll(), intervalMs);
    await this.poll();
  }

  public stop() {
    this.isPolling = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    console.log("[EventPoller] Polling stopped");
  }

  public async poll(): Promise<PolledEvent[]> {
    if (!this.contractIds.length) return [];

    const foundEvents: PolledEvent[] = [];
    try {
      const res = await this.server.getEvents({
        startLedger: this.lastLedger,
        filters: [
          {
            type: "contract",
            contractIds: this.contractIds,
          },
        ],
        limit: 50,
      });

      if (res.events && res.events.length > 0) {
        for (const ev of res.events) {
          const topics = ev.topic.map((t) => {
            try {
              return String(scValToNative(t));
            } catch {
              return t.toXDR("base64");
            }
          });

          let data: any = null;
          try {
            data = scValToNative(ev.value);
          } catch {
            data = ev.value.toXDR("base64");
          }

          const contractIdStr = ev.contractId
            ? (typeof ev.contractId === "string" ? ev.contractId : (ev.contractId as any).contractId ? (ev.contractId as any).contractId() : String(ev.contractId))
            : "";

          const parsed: PolledEvent = {
            id: ev.id,
            contractId: contractIdStr,
            ledger: ev.ledger,
            ledgerClosedAt: ev.ledgerClosedAt,
            topic: topics,
            data,
          };

          foundEvents.push(parsed);
          this.listeners.forEach((listener) => listener(parsed));

          if (ev.ledger > this.lastLedger) {
            this.lastLedger = ev.ledger + 1;
          }
        }
      }
    } catch (error) {
      console.error("[EventPoller] Error polling Soroban events:", error);
    }

    return foundEvents;
  }
}
