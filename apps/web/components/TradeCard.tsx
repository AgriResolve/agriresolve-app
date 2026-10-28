"use client";

import Link from "next/link";
import { TradeDetails, formatStroops, shortenAddress, getStateBadge } from "../lib/stellar";
import { ArrowUpRight, Clock, ShieldAlert, CheckCircle2 } from "lucide-react";

interface TradeCardProps {
  trade: TradeDetails;
}

export function TradeCard({ trade }: TradeCardProps) {
  const badge = getStateBadge(trade.state);

  return (
    <div className="bg-zinc-900/60 border border-zinc-800/80 hover:border-emerald-500/40 rounded-xl p-5 transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              #{trade.id}
            </span>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${badge.color}`}
            >
              {badge.label}
            </span>
          </div>
          <span className="text-xs text-zinc-500 font-mono">
            {new Date(trade.createdAt * 1000).toLocaleDateString()}
          </span>
        </div>

        <div className="mb-4">
          <div className="text-2xl font-bold text-zinc-100 flex items-baseline gap-1.5">
            {formatStroops(trade.amount)}
            <span className="text-xs font-semibold text-emerald-400">USDC</span>
          </div>
        </div>

        <div className="space-y-2 text-xs border-t border-zinc-800/60 pt-3">
          <div className="flex justify-between items-center text-zinc-400">
            <span>Buyer:</span>
            <span className="font-mono text-zinc-200">{shortenAddress(trade.buyer)}</span>
          </div>
          <div className="flex justify-between items-center text-zinc-400">
            <span>Farmer:</span>
            <span className="font-mono text-zinc-200">{shortenAddress(trade.farmer)}</span>
          </div>
          <div className="flex justify-between items-center text-zinc-400">
            <span>Arbiter:</span>
            <span className="font-mono text-zinc-400">{shortenAddress(trade.arbiter)}</span>
          </div>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-zinc-800/60">
        <Link
          href={`/trade/${trade.id}`}
          className="flex items-center justify-center gap-1.5 w-full py-2 px-3 rounded-lg bg-zinc-800 hover:bg-emerald-600 hover:text-zinc-950 text-xs font-medium text-zinc-200 transition-colors"
        >
          <span>Manage Trade</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
