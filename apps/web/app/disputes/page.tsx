"use client";

import Link from "next/link";
import { ArrowLeft, FileText, Cpu, CheckCircle2, ShieldAlert } from "lucide-react";
import { EvidenceUploader } from "../../components/EvidenceUploader";

export default function DisputesPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-emerald-400 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-2 text-emerald-400">
          <FileText className="w-5 h-5" />
          <h1 className="text-xl font-bold text-zinc-100">AI Dispute Evidence Evaluation</h1>
        </div>
        <p className="text-xs text-zinc-400 mb-6">
          The AgriResolve AI pipeline uses a Meterless World Model to parse multi-party agricultural
          documentation, detects contract discrepancies (such as allowable moisture shrinkage vs weight loss),
          and compiles on-chain dispute resolution proofs.
        </p>

        <EvidenceUploader escrowId={2} />
      </div>

      <div className="p-6 rounded-2xl bg-zinc-900/40 border border-zinc-800 text-xs space-y-4">
        <h3 className="font-semibold text-zinc-200 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-400" />
          Off-Chain AI Provenance Pipeline Architecture
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <span className="font-medium text-emerald-400 block mb-1">1. Claim Extraction</span>
            <span className="text-zinc-400">
              Parses weighbridge tickets and moisture certificates into bounds and claims.
            </span>
          </div>
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <span className="font-medium text-emerald-400 block mb-1">2. Contradiction Audit</span>
            <span className="text-zinc-400">
              Llama-3.1-Nemotron reconciles trade discrepancies against contract bylaws.
            </span>
          </div>
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <span className="font-medium text-emerald-400 block mb-1">3. Soroban Settlement</span>
            <span className="text-zinc-400">
              Emits signed split payout parameters to execute on-chain escrow resolution.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
