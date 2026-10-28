export const NETWORK_CONFIG = {
  rpcUrl: process.env.NEXT_PUBLIC_RPC_URL || "https://soroban-testnet.stellar.org",
  networkPassphrase: process.env.NEXT_PUBLIC_NETWORK_PASSPHRASE || "Test SDF Network ; September 2015",
  contractId: process.env.NEXT_PUBLIC_CONTRACT_ID || "CAPZ2NHR5OYR45WH4BBFVKRG2UYII6P3DD3JNP6CJ6LQ4GJDZVOGITQ4",
  usdcAddress: process.env.NEXT_PUBLIC_USDC_ADDRESS || "CCQGOTGN6HTQE74XYERYSYVU57T5NPYWV5DLCROMB56OXTV6RSO6KIGK",
};

export enum EscrowState {
  Funded = 0,
  Delivered = 1,
  Disputed = 2,
  Resolved = 3,
  Refunded = 4,
}

export interface TradeDetails {
  id: number;
  buyer: string;
  farmer: string;
  arbiter: string;
  token: string;
  amount: number;
  state: EscrowState;
  deliveryHash?: string;
  expiry: number;
  buyerShare: number;
  farmerShare: number;
  createdAt: number;
}

export function formatStroops(amount: number): string {
  return (amount / 10_000_000).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
}

export function parseToStroops(amount: string | number): number {
  return Math.round(Number(amount) * 10_000_000);
}

export function shortenAddress(addr: string): string {
  if (!addr || addr.length < 10) return addr;
  return `${addr.slice(0, 4)}...${addr.slice(-4)}`;
}

export function getStateBadge(state: EscrowState): { label: string; color: string } {
  switch (state) {
    case EscrowState.Funded:
      return { label: "Funded", color: "bg-blue-500/20 text-blue-400 border-blue-500/30" };
    case EscrowState.Delivered:
      return { label: "Delivered", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" };
    case EscrowState.Disputed:
      return { label: "Disputed", color: "bg-amber-500/20 text-amber-400 border-amber-500/30" };
    case EscrowState.Resolved:
      return { label: "Resolved", color: "bg-purple-500/20 text-purple-400 border-purple-500/30" };
    case EscrowState.Refunded:
      return { label: "Refunded", color: "bg-zinc-500/20 text-zinc-400 border-zinc-500/30" };
    default:
      return { label: "Unknown", color: "bg-zinc-800 text-zinc-400 border-zinc-700" };
  }
}
