"use client";

import { useState } from "react";
import { CheckCircle2, ShieldAlert, Cpu, X, ArrowRight, Loader2 } from "lucide-react";

interface ResolutionModalProps {
  isOpen: boolean;
  onClose: () => void;
  escrowId: number;
  totalAmount: number;
  buyerShare: number;
  farmerShare: number;
  proofHash?: string;
  onExecuted?: () => void;
}

export function ResolutionModal({
  isOpen,
  onClose,
  escrowId,
  totalAmount,
  buyerShare,
  farmerShare,
  proofHash,
  onExecuted,
}: ResolutionModalProps) {
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  async function handleExecute() {
    setSubmitting(true);
    try {
      // Simulate on-chain contract call execute_resolution(arbiter, escrow_id, buyer_share, farmer_share)
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setSuccess(true);
      if (onExecuted) onExecuted();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-emerald-500/30 rounded-2xl max-w-lg w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-200"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-4 text-emerald-400">
          <ShieldAlert className="w-6 h-6" />
          <h3 className="text-lg font-bold text-zinc-100">Execute Dispute Resolution</h3>
        </div>

        <p className="text-xs text-zinc-400 mb-6">
          This triggers the Soroban <code className="text-emerald-300">execute_resolution</code> function.
          Balances will be atomically distributed to the buyer and farmer wallets via the SAC Token Client.
        </p>

        <div className="bg-zinc-950 rounded-xl p-4 border border-zinc-800 space-y-3 mb-6">
          <div className="flex justify-between items-center text-xs">
            <span className="text-zinc-400">Escrow ID:</span>
            <span className="font-mono text-zinc-200">#{escrowId}</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-zinc-400">Total Escrow Amount:</span>
            <span className="font-mono text-zinc-200">{(totalAmount / 10_000_000).toFixed(2)} USDC</span>
          </div>
          <div className="flex justify-between items-center text-xs text-emerald-400 font-semibold border-t border-zinc-800 pt-2">
            <span>Buyer Split:</span>
            <span className="font-mono">{(buyerShare / 10_000_000).toFixed(2)} USDC</span>
          </div>
          <div className="flex justify-between items-center text-xs text-emerald-400 font-semibold">
            <span>Farmer Split:</span>
            <span className="font-mono">{(farmerShare / 10_000_000).toFixed(2)} USDC</span>
          </div>
          {proofHash && (
            <div className="pt-2 border-t border-zinc-800">
              <span className="text-[11px] text-zinc-500 block mb-1">Attached Off-Chain Audit Hash:</span>
              <span className="font-mono text-[10px] text-zinc-400 break-all">{proofHash}</span>
            </div>
          )}
        </div>

        {success ? (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs text-center space-y-3">
            <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400" />
            <p className="font-semibold text-sm">Resolution Successfully Executed On-Chain!</p>
            <p className="text-zinc-400">Tokens have been atomically settled and trade status updated to Resolved.</p>
            <button
              onClick={onClose}
              className="mt-2 py-2 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-semibold text-xs"
            >
              Close
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              disabled={submitting}
              className="flex-1 py-2.5 px-4 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-medium text-xs transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleExecute}
              disabled={submitting}
              className="flex-1 py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-sm shadow-emerald-950"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Submitting to Stellar...</span>
                </>
              ) : (
                <>
                  <span>Confirm Settlement</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
