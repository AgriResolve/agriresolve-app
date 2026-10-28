"use client";

import Link from "next/link";
import { WalletConnect } from "./WalletConnect";
import { Sprout, ShieldCheck, FileText, PlusCircle } from "lucide-react";

export function Navbar() {
  return (
    <header className="border-b border-emerald-950/40 bg-zinc-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-lg text-emerald-300">AgriResolve</span>
              <span className="text-xs block text-emerald-600 font-mono">Soroban Escrow Protocol</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link
              href="/"
              className="text-zinc-400 hover:text-emerald-400 transition-colors flex items-center gap-1.5"
            >
              <ShieldCheck className="w-4 h-4" />
              Escrows
            </Link>
            <Link
              href="/trade/new"
              className="text-zinc-400 hover:text-emerald-400 transition-colors flex items-center gap-1.5"
            >
              <PlusCircle className="w-4 h-4" />
              New Trade
            </Link>
            <Link
              href="/disputes"
              className="text-zinc-400 hover:text-emerald-400 transition-colors flex items-center gap-1.5"
            >
              <FileText className="w-4 h-4" />
              AI Evidence & Disputes
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <WalletConnect />
        </div>
      </div>
    </header>
  );
}
