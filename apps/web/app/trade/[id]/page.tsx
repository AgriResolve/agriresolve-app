"use client";

import { use, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ShieldAlert, CheckCircle2, Clock, Truck, RefreshCw, AlertTriangle, ArrowRight } from "lucide-react";
import { formatStroops, getStateBadge, shortenAddress, EscrowState, TradeDetails } from "../../../lib/stellar";
import { ResolutionModal } from "../../../components/ResolutionModal";
import { EvidenceUploader } from "../../../components/EvidenceUploader";

export default function TradeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const tradeId = Number(resolvedParams.id);

  const [trade, setTrade] = useState<TradeDetails>({
    id: tradeId,
    buyer: "GAHYU5YGHEOI3MKA2MLW2O46YY74SHBLC4JTVGWN36LH7LL7FFF4O6SS",
    farmer: "GBV4X4M4R5VTYOUCYA3E62L6JCG37VHYK2YGB6U2NZZK3J6D22A7KOR2",
    arbiter: "GCS3ZJ46V3K2LL6A5Z9Z4K2M3G4N5B6V7C8X9Z0A1S2D3F4G5H6J7K8L",
    token: "CCQGOTGN6HTQE74XYERYSYVU57T5NPYWV5DLCROMB56OXTV6RSO6KIGK",
    amount: 10_000_000, // 1.0 USDC
    state: EscrowState.Disputed,
    deliveryHash: "84f9cfa549c318847d1cede87688c73cf9d125893c3a5a90ba74b82c5e325565",
    expiry: Math.floor(Date.now() / 1000) + 86400 * 3,
    buyerShare: 6_000_000,
    farmerShare: 4_000_000,
    createdAt: Math.floor(Date.now() / 1000) - 86400 * 2,
  });

  const [isResolutionOpen, setIsResolutionOpen] = useState(false);
  const [deliveryHashInput, setDeliveryHashInput] = useState("");
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const badge = getStateBadge(trade.state);

  function handleFlagDispute() {
    setTrade((prev) => ({ ...prev, state: EscrowState.Disputed }));
    setActionSuccess("Dispute flagged successfully on-chain! Funds are locked pending AI resolution.");
  }

  function handleConfirmDelivery() {
    const hash = deliveryHashInput || "84f9cfa549c318847d1cede87688c73cf9d125893c3a5a90ba74b82c5e325565";
    setTrade((prev) => ({ ...prev, state: EscrowState.Delivered, deliveryHash: hash }));
    setActionSuccess("Delivery confirmation hash recorded on Stellar Testnet!");
  }

  function handleRefund() {
    setTrade((prev) => ({ ...prev, state: EscrowState.Refunded, buyerShare: prev.amount, farmerShare: 0 }));
    setActionSuccess("Full refund processed back to buyer.");
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-emerald-400 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Main Trade Header */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-6 border-b border-zinc-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-2xl font-bold text-zinc-100">Trade Escrow #{trade.id}</h1>
              <span className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${badge.color}`}>
                {badge.label}
              </span>
            </div>
            <p className="text-xs text-zinc-500 font-mono">
              Created on {new Date(trade.createdAt * 1000).toLocaleString()}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-zinc-400 block mb-1">Locked Amount</span>
            <div className="text-3xl font-extrabold text-zinc-100">
              {formatStroops(trade.amount)} <span className="text-sm text-emerald-400 font-semibold">USDC</span>
            </div>
          </div>
        </div>

        {actionSuccess && (
          <div className="mb-6 flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Trade Details Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs mb-8">
          <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80">
            <span className="text-zinc-500 block mb-1">Buyer Address</span>
            <span className="font-mono text-zinc-200">{trade.buyer}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80">
            <span className="text-zinc-500 block mb-1">Farmer Address</span>
            <span className="font-mono text-zinc-200">{trade.farmer}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80">
            <span className="text-zinc-500 block mb-1">Arbiter / AI Multisig</span>
            <span className="font-mono text-zinc-200">{trade.arbiter}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80">
            <span className="text-zinc-500 block mb-1">Expiry Date</span>
            <span className="font-mono text-zinc-200">
              {new Date(trade.expiry * 1000).toLocaleString()}
            </span>
          </div>
        </div>

        {trade.deliveryHash && (
          <div className="mb-8 p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80 text-xs">
            <span className="text-zinc-500 block mb-1">On-Chain Delivery Confirmation Hash:</span>
            <span className="font-mono text-[11px] text-emerald-400 break-all">{trade.deliveryHash}</span>
          </div>
        )}

        {/* Action Controls */}
        <div className="border-t border-zinc-800 pt-6">
          <h3 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-4">
            Interactive State Machine Actions
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {trade.state === EscrowState.Funded && (
              <>
                <button
                  onClick={handleConfirmDelivery}
                  className="py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-semibold text-xs flex items-center justify-center gap-2"
                >
                  <Truck className="w-4 h-4" />
                  <span>Confirm Delivery (Farmer)</span>
                </button>
                <button
                  onClick={handleRefund}
                  className="py-2.5 px-4 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold text-xs flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Cancel & Refund (Buyer)</span>
                </button>
              </>
            )}

            {(trade.state === EscrowState.Funded || trade.state === EscrowState.Delivered) && (
              <button
                onClick={handleFlagDispute}
                className="py-2.5 px-4 rounded-lg bg-amber-600 hover:bg-amber-500 text-zinc-950 font-semibold text-xs flex items-center justify-center gap-2"
              >
                <AlertTriangle className="w-4 h-4" />
                <span>Flag Non-Compliance Dispute</span>
              </button>
            )}

            {trade.state === EscrowState.Disputed && (
              <button
                onClick={() => setIsResolutionOpen(true)}
                className="col-span-full py-3 px-4 rounded-lg bg-purple-600 hover:bg-purple-500 text-zinc-950 font-bold text-xs flex items-center justify-center gap-2 shadow-sm shadow-purple-950"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>Execute AI Arbiter Resolution ({formatStroops(trade.buyerShare)} / {formatStroops(trade.farmerShare)} USDC Split)</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Embedded Evidence & Provenance Pipeline */}
      {trade.state === EscrowState.Disputed && (
        <EvidenceUploader
          escrowId={trade.id}
          onAnalysisComplete={(res) => {
            if (res.proof) {
              setTrade((prev) => ({
                ...prev,
                buyerShare: res.proof.buyer_share,
                farmerShare: res.proof.farmer_share,
              }));
            }
          }}
        />
      )}

      {/* Resolution Execution Modal */}
      <ResolutionModal
        isOpen={isResolutionOpen}
        onClose={() => setIsResolutionOpen(false)}
        escrowId={trade.id}
        totalAmount={trade.amount}
        buyerShare={trade.buyerShare}
        farmerShare={trade.farmerShare}
        onExecuted={() => {
          setTrade((prev) => ({ ...prev, state: EscrowState.Resolved }));
          setActionSuccess("Dispute finalized and settled atomically on Stellar Testnet!");
        }}
      />
    </div>
  );
}
