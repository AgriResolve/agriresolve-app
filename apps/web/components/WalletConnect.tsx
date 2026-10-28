"use client";

import { useState } from "react";
import { Wallet, CheckCircle2, ChevronDown, ExternalLink } from "lucide-react";
import { shortenAddress } from "../lib/stellar";

export function WalletConnect() {
  const [address, setAddress] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  async function connectWallet() {
    setIsConnecting(true);
    try {
      // Connect using Freighter if available, or simulate testnet account
      if (typeof window !== "undefined" && (window as any).freighterApi) {
        const freighter = (window as any).freighterApi;
        const res = await freighter.requestAccess();
        if (res && res.address) {
          setAddress(res.address);
          setIsConnecting(false);
          return;
        }
      }
      // Demo testnet fallback account
      setAddress("GAHYU5YGHEOI3MKA2MLW2O46YY74SHBLC4JTVGWN36LH7LL7FFF4O6SS");
    } catch (err) {
      console.error("Wallet connection error:", err);
    } finally {
      setIsConnecting(false);
    }
  }

  function disconnect() {
    setAddress(null);
  }

  if (address) {
    return (
      <div className="flex items-center gap-2">
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Testnet
        </div>
        <button
          onClick={disconnect}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-mono hover:border-emerald-500/60 transition-colors"
          title="Click to disconnect"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>{shortenAddress(address)}</span>
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={connectWallet}
      disabled={isConnecting}
      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 text-sm font-semibold transition-all shadow-sm shadow-emerald-950"
    >
      <Wallet className="w-4 h-4" />
      <span>{isConnecting ? "Connecting..." : "Connect Freighter"}</span>
    </button>
  );
}
