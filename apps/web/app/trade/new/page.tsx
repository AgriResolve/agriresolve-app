"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ShieldCheck, PlusCircle, AlertCircle, Loader2 } from "lucide-react";
import { NETWORK_CONFIG, parseToStroops } from "../../../lib/stellar";

export default function NewTradePage() {
  const router = useRouter();
  const [farmer, setFarmer] = useState("GBJ5W4M4R5VTYOUCYA3E62L6JCG37VHYK2YGB6U2NZZK3J6D22A7FARM");
  const [arbiter, setArbiter] = useState("GCS3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7K8L");
  const [token, setToken] = useState(NETWORK_CONFIG.usdcAddress);
  const [amount, setAmount] = useState("10.0");
  const [durationDays, setDurationDays] = useState("14");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (!farmer || farmer.length < 50) {
        throw new Error("Invalid Farmer Stellar address");
      }
      if (!amount || Number(amount) <= 0) {
        throw new Error("Amount must be greater than 0");
      }

      // Simulate on-chain initialize_trade transaction
      await new Promise((resolve) => setTimeout(resolve, 1500));

      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to initialize trade");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-emerald-400 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-2 text-emerald-400">
          <ShieldCheck className="w-5 h-5" />
          <h1 className="text-xl font-bold text-zinc-100">Initiate Agricultural Escrow</h1>
        </div>
        <p className="text-xs text-zinc-400 mb-6">
          Fund tokens into the Soroban escrow contract. Collateral remains locked until delivery is
          confirmed or any dispute is reconciled by off-chain AI analysis.
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
              Farmer / Seller Stellar Address
            </label>
            <input
              type="text"
              value={farmer}
              onChange={(e) => setFarmer(e.target.value)}
              required
              placeholder="G..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
              Arbiter / Oracle Multi-Sig Address
            </label>
            <input
              type="text"
              value={arbiter}
              onChange={(e) => setArbiter(e.target.value)}
              required
              placeholder="G..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
                Escrow Amount (USDC)
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.01"
                  min="0.1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-3.5 pr-14 py-2.5 text-sm font-semibold text-zinc-100 focus:outline-none focus:border-emerald-500"
                />
                <span className="absolute right-3.5 top-2.5 text-xs font-bold text-emerald-400">
                  USDC
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
                Lockup Expiry (Days)
              </label>
              <input
                type="number"
                min="1"
                max="90"
                value={durationDays}
                onChange={(e) => setDurationDays(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
              Settlement Token Address (SEP-41)
            </label>
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-xs font-mono text-zinc-400 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-sm shadow-emerald-950"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Authorizing Deposit & Opening Escrow...</span>
                </>
              ) : (
                <>
                  <PlusCircle className="w-4 h-4" />
                  <span>Lock Collateral & Open Escrow</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
