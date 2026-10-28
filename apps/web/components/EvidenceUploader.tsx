"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle2, AlertCircle, FileText, Cpu, ArrowRight } from "lucide-react";

interface EvidenceUploaderProps {
  escrowId?: number;
  onAnalysisComplete?: (result: any) => void;
}

export function EvidenceUploader({ escrowId = 1, onAnalysisComplete }: EvidenceUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [scenario, setScenario] = useState("DISP-MAIZE-002-DISPUTE");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setAnalyzing(true);
    setError(null);
    try {
      const res = await fetch("/api/disputes/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dispute_id: scenario,
          escrow_id: escrowId,
          amount: 10_000_000,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Analysis failed");
      }
      setAnalysisResult(data);
      if (onAnalysisComplete) {
        onAnalysisComplete(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to analyze evidence");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4 text-emerald-400">
        <UploadCloud className="w-5 h-5" />
        <h3 className="font-semibold text-zinc-100">AI Dispute Evidence Intake</h3>
      </div>
      <p className="text-xs text-zinc-400 mb-5">
        Upload harvest manifests, weighbridge tickets, or moisture certificates. The off-chain
        Nemotron investigation pipeline reconciles contradictions and formats cryptographic split resolution proofs for contract execution.
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-zinc-300 mb-1.5">
            Select Dispute Scenario / Evidence Package:
          </label>
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="DISP-MAIZE-002-DISPUTE">
              DISP-002: Core MVP (Quantity shortfall, moisture shrinkage 14.8% vs 13.5%)
            </option>
            <option value="DISP-MAIZE-003-MISSING-INSPECTION">
              DISP-003: Actionable Evidence Request (Missing destination cert)
            </option>
            <option value="DISP-MAIZE-004-CONFLICTING-RECORDS">
              DISP-004: Conflicting Records (Weighbridge discrepancy)
            </option>
          </select>
        </div>

        <div className="border-2 border-dashed border-zinc-800 hover:border-emerald-500/50 rounded-xl p-6 text-center cursor-pointer transition-colors bg-zinc-950/40">
          <FileText className="w-8 h-8 text-zinc-500 mx-auto mb-2" />
          <p className="text-xs text-zinc-300 font-medium">
            Drag and drop inspection PDF / weighbridge receipt, or click to browse
          </p>
          <p className="text-[11px] text-zinc-500 mt-1">Accepts PDF, PNG, JPG up to 15MB</p>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-sm shadow-emerald-950"
        >
          <Cpu className="w-4 h-4" />
          <span>{analyzing ? "Investigating Off-Chain Evidence..." : "Run AI Evidence Audit"}</span>
        </button>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {analysisResult && (
          <div className="mt-4 p-4 rounded-xl bg-zinc-950 border border-emerald-500/30 text-xs space-y-3">
            <div className="flex items-center justify-between text-emerald-400 font-medium border-b border-zinc-800 pb-2">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Audit Complete
              </span>
              <span className="font-mono text-zinc-400">Escrow #{escrowId}</span>
            </div>

            <div>
              <span className="text-zinc-500 block mb-1">Reasoning Summary:</span>
              <p className="text-zinc-300 bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                {analysisResult.proof.reasoning_summary}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                <span className="text-zinc-500 block">Buyer Refund Share</span>
                <span className="text-sm font-bold text-emerald-400">
                  {(analysisResult.proof.buyer_share / 10_000_000).toFixed(2)} USDC
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                <span className="text-zinc-500 block">Farmer Payout Share</span>
                <span className="text-sm font-bold text-emerald-400">
                  {(analysisResult.proof.farmer_share / 10_000_000).toFixed(2)} USDC
                </span>
              </div>
            </div>

            <div className="pt-1">
              <span className="text-zinc-500 block text-[11px] mb-1">Auditor Cryptographic Hash:</span>
              <span className="font-mono text-[10px] text-zinc-400 break-all block bg-zinc-900 p-1.5 rounded">
                {analysisResult.proof.auditor_signature}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
