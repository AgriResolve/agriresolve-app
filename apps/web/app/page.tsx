"use client";

import { useState } from "react";
import Link from "next/link";
import { TradeCard } from "../components/TradeCard";
import { EscrowState, TradeDetails } from "../lib/stellar";
import { ShieldCheck, PlusCircle, FileText, ArrowRight, TrendingUp, AlertTriangle } from "lucide-react";

const DEMO_TRADES: TradeDetails[] = [
  {
    id: 1,
    buyer: "GAHYU5YGHEOI3MKA2MLW2O46YY74SHBLC4JTVGWN36LH7LL7FFF4O6SS",
    farmer: "GBJ5W4M4R5VTYOUCYA3E62L6JCG37VHYK2YGB6U2NZZK3J6D22A7FARM",
    arbiter: "GCS3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7K8L",
    token: "CCQGOTGN6HTQE74XYERYSYVU57T5NPYWV5DLCROMB56OXTV6RSO6KIGK",
    amount: 15_000_000, // 1.5 USDC
    state: EscrowState.Funded,
    expiry: Math.floor(Date.now() / 1000) + 86400 * 7,
    buyerShare: 0,
    farmerShare: 0,
    createdAt: Math.floor(Date.now() / 1000) - 3600 * 4,
  },
  {
    id: 2,
    buyer: "GAHYU5YGHEOI3MKA2MLW2O46YY74SHBLC4JTVGWN36LH7LL7FFF4O6SS",
    farmer: "GBV4X4M4R5VTYOUCYA3E62L6JCG37VHYK2YGB6U2NZZK3J6D22A7KOR2",
    arbiter: "GCS3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7K8L",
    token: "CCQGOTGN6HTQE74XYERYSYVU57T5NPYWV5DLCROMB56OXTV6RSO6KIGK",
    amount: 10_000_000, // 1.0 USDC
    state: EscrowState.Disputed,
    deliveryHash: "84f9cfa549c318847d1cede87688c73cf9d125893c3a5a90ba74b82c5e325565",
    expiry: Math.floor(Date.now() / 1000) + 86400 * 3,
    buyerShare: 0,
    farmerShare: 0,
    createdAt: Math.floor(Date.now() / 1000) - 86400 * 2,
  },
  {
    id: 3,
    buyer: "GDK3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7BUY3",
    farmer: "GBJ5W4M4R5VTYOUCYA3E62L6JCG37VHYK2YGB6U2NZZK3J6D22A7FARM",
    arbiter: "GCS3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7K8L",
    token: "CCQGOTGN6HTQE74XYERYSYVU57T5NPYWV5DLCROMB56OXTV6RSO6KIGK",
    amount: 25_000_000, // 2.5 USDC
    state: EscrowState.Resolved,
    deliveryHash: "a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
    expiry: Math.floor(Date.now() / 1000) - 3600,
    buyerShare: 15_000_000,
    farmerShare: 10_000_000,
    createdAt: Math.floor(Date.now() / 1000) - 86400 * 5,
  },
];

export default function HomePage() {
  const [filter, setFilter] = useState<string>("all");

  const filteredTrades = DEMO_TRADES.filter((trade) => {
    if (filter === "disputed") return trade.state === EscrowState.Disputed;
    if (filter === "active") return trade.state === EscrowState.Funded || trade.state === EscrowState.Delivered;
    if (filter === "resolved") return trade.state === EscrowState.Resolved;
    return true;
  });

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="rounded-2xl bg-gradient-to-br from-emerald-950/40 via-zinc-900 to-zinc-950 border border-emerald-500/20 p-8 relative overflow-hidden">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium mb-4">
            <ShieldCheck className="w-3.5 h-3.5" />
            Soroban Agricultural Escrow State Machine
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-zinc-100 tracking-tight mb-3">
            Load-Bearing Blockchain Escrow with AI Dispute Resolution
          </h1>
          <p className="text-sm text-zinc-400 leading-relaxed mb-6">
            Lock agricultural trade capital on Stellar. When disputes arise over moisture, quality,
            or weight, off-chain Llama-3.1-Nemotron agents investigate evidence provenance,
            cryptographically authorizing atomic split payouts.
          </p>

          <div className="flex flex-wrap gap-3">
            <Link
              href="/trade/new"
              className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 text-sm font-semibold flex items-center gap-2 transition-all shadow-sm shadow-emerald-950"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Initiate New Trade</span>
            </Link>
            <Link
              href="/disputes"
              className="px-5 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-semibold flex items-center gap-2 transition-colors border border-zinc-700"
            >
              <FileText className="w-4 h-4" />
              <span>AI Evidence Intake</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Protocol Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800">
          <div className="text-xs text-zinc-400 mb-1 flex items-center justify-between">
            <span>Total Value Escrowed</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-zinc-100">50.00 <span className="text-xs text-emerald-400">USDC</span></div>
          <div className="text-[11px] text-zinc-500 mt-1">Across active agricultural trades</div>
        </div>

        <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800">
          <div className="text-xs text-zinc-400 mb-1 flex items-center justify-between">
            <span>Active Disputes</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">1 Case</div>
          <div className="text-[11px] text-zinc-500 mt-1">Under autonomous AI audit</div>
        </div>

        <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800">
          <div className="text-xs text-zinc-400 mb-1 flex items-center justify-between">
            <span>Settlement Time</span>
            <ShieldCheck className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-purple-300">&lt; 5 Seconds</div>
          <div className="text-[11px] text-zinc-500 mt-1">Stellar Testnet ledger finality</div>
        </div>
      </div>

      {/* Trades Dashboard Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-zinc-100">Escrow Trades</h2>
            <p className="text-xs text-zinc-400">Monitor active, disputed, and resolved trade contracts</p>
          </div>

          <div className="flex items-center gap-1.5 bg-zinc-900 p-1 rounded-lg border border-zinc-800 text-xs">
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1 rounded-md transition-colors ${
                filter === "all" ? "bg-emerald-600 text-zinc-950 font-semibold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter("active")}
              className={`px-3 py-1 rounded-md transition-colors ${
                filter === "active" ? "bg-emerald-600 text-zinc-950 font-semibold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Active
            </button>
            <button
              onClick={() => setFilter("disputed")}
              className={`px-3 py-1 rounded-md transition-colors ${
                filter === "disputed" ? "bg-emerald-600 text-zinc-950 font-semibold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Disputed
            </button>
            <button
              onClick={() => setFilter("resolved")}
              className={`px-3 py-1 rounded-md transition-colors ${
                filter === "resolved" ? "bg-emerald-600 text-zinc-950 font-semibold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Resolved
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredTrades.map((trade) => (
            <TradeCard key={trade.id} trade={trade} />
          ))}
        </div>
      </div>
    </div>
  );
}
