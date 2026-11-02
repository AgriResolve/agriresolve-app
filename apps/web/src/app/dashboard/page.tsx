"use client";

import { useState } from "react";
import Link from "next/link";
import EscrowStepper, { EscrowStep } from "@/components/EscrowStepper";
import EvidenceUploader from "@/components/EvidenceUploader";
import TradeDetailsPanel, { TradeSummary } from "@/components/TradeDetailsPanel";
import { connectFreighter } from "@/lib/wallet";

export default function DashboardPage() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [activeTab, setActiveTab] = useState<"trades" | "disputes" | "standards">("trades");
  const [currentStep, setCurrentStep] = useState<EscrowStep>("Disputed");
  const [notification, setNotification] = useState<string | null>(null);

  const sampleTrade: TradeSummary = {
    tradeId: "1049",
    buyerAddress: "GDQP2KPQGKIW5LU7WJY7RA2K2CST6VNEJ5QO4GBL3H3AEXK4L3377777",
    farmerAddress: "GBXGQJWVLWOYHFLVTKWV5FGHA3LNYY2JQW3W4K477777777777777777",
    amount: "10,000.00",
    tokenSymbol: "USDC",
    commodityGrade: "Grade 1 White Maize (Base 12.0%)",
    contractQuantity: "50.00 MT (50,000 kg)",
    expiryDate: "2026-11-30 23:59 UTC",
  };

  const handleConnectWallet = async () => {
    setIsConnecting(true);
    try {
      const address = await connectFreighter();
      setWalletAddress(address);
      setNotification(`Connected wallet: ${address.slice(0, 6)}...${address.slice(-6)}`);
      setTimeout(() => setNotification(null), 3000);
    } catch (err: any) {
      alert(`Could not connect Freighter: ${err.message}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleStepTransition = (nextStep: EscrowStep) => {
    setCurrentStep(nextStep);
    setNotification(`Escrow status updated to: ${nextStep}`);
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="min-h-screen bg-[#F4F7F4] flex flex-col text-stone-900 font-sans">
      {/* Top Header */}
      <header className="w-full bg-white border-b border-[#D1D9D1] px-6 h-16 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-[#1E4D2B] flex items-center justify-center rounded text-white font-bold text-lg">
              A
            </div>
            <span className="font-bold text-lg tracking-tight text-stone-900">
              AgriResolve
            </span>
          </Link>
          <span className="text-xs px-2 py-0.5 bg-stone-100 border border-[#D1D9D1] rounded text-stone-600 font-mono">
            TESTNET (Protocol 22/29)
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {notification && (
            <span className="text-xs font-semibold text-[#1E4D2B] bg-[#EBF3EC] px-2.5 py-1 rounded border border-[#D1D9D1]">
              {notification}
            </span>
          )}

          {walletAddress ? (
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-stone-100 border border-[#D1D9D1] rounded font-mono text-xs text-stone-800">
              <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block" />
              <span>{walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}</span>
            </div>
          ) : (
            <button
              onClick={handleConnectWallet}
              disabled={isConnecting}
              className="bg-[#1E4D2B] hover:bg-[#14371E] text-white text-xs font-semibold px-4 py-2 rounded transition-colors"
            >
              {isConnecting ? "Connecting..." : "Connect Wallet"}
            </button>
          )}
        </div>
      </header>

      {/* Main Body with Sidebar */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto p-6 gap-6">
        {/* Left Sidebar */}
        <aside className="w-60 bg-white border border-[#D1D9D1] rounded p-4 flex flex-col justify-between shrink-0 h-[calc(100vh-7rem)] sticky top-20">
          <div className="space-y-1">
            <div className="text-[11px] font-bold text-stone-400 uppercase tracking-wider px-3 py-2">
              Management
            </div>
            <button
              onClick={() => setActiveTab("trades")}
              className={`w-full text-left px-3 py-2 rounded text-xs font-semibold transition-colors ${
                activeTab === "trades"
                  ? "bg-[#1E4D2B] text-white"
                  : "text-stone-700 hover:bg-stone-100"
              }`}
            >
              Active Deals (1)
            </button>
            <button
              onClick={() => setActiveTab("disputes")}
              className={`w-full text-left px-3 py-2 rounded text-xs font-semibold transition-colors ${
                activeTab === "disputes"
                  ? "bg-[#1E4D2B] text-white"
                  : "text-stone-700 hover:bg-stone-100"
              }`}
            >
              Dispute Dossiers
            </button>
            <button
              onClick={() => setActiveTab("standards")}
              className={`w-full text-left px-3 py-2 rounded text-xs font-semibold transition-colors ${
                activeTab === "standards"
                  ? "bg-[#1E4D2B] text-white"
                  : "text-stone-700 hover:bg-stone-100"
              }`}
            >
              Crop Standards
            </button>
          </div>

          <div className="border-t border-[#D1D9D1] pt-4 space-y-2 text-xs text-stone-500">
            <div className="text-[11px] font-bold uppercase tracking-wider text-stone-400">
              Live Contracts
            </div>
            <div className="font-mono text-[10px] truncate" title="CC3OJZP4DCYOOTRJTT66UHMAGR2677JNDBNFQYMREQA2ONDWNRAO75J6">
              Reg: CC3OJZ...75J6
            </div>
            <div className="font-mono text-[10px] truncate" title="CCPZFPNUQGNT5O6H3VWT2H23CLXF2POF5QYDAD4HPOB2RRKSHO63OIXC">
              Esc: CCPZFP...OIXC
            </div>
            <div className="font-mono text-[10px] truncate" title="CCBQBMQFQPRRMOQLPNYSIBGTL7AOXXQAAIADXE2YYTZHSUSDS6Z4ES5N">
              Dsp: CCBQBM...ES5N
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 space-y-6">
          {/* Stepper */}
          <EscrowStepper currentStep={currentStep} />

          {/* Trade Details Panel */}
          <TradeDetailsPanel trade={sampleTrade} />

          {/* Trade Lifecycle Action Bar */}
          <div className="bg-white border border-[#D1D9D1] p-4 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="font-medium text-stone-600">
              Actions for Current State (<span className="font-bold text-stone-900">{currentStep}</span>):
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleStepTransition("Delivered")}
                className="px-3 py-2 bg-stone-100 hover:bg-stone-200 border border-[#D1D9D1] font-semibold text-stone-800 rounded transition-colors"
              >
                Confirm Delivery
              </button>
              <button
                onClick={() => handleStepTransition("Disputed")}
                className="px-3 py-2 bg-stone-100 hover:bg-stone-200 border border-[#D1D9D1] font-semibold text-stone-800 rounded transition-colors"
              >
                Flag Dispute
              </button>
              <button
                onClick={() => handleStepTransition("Resolved")}
                className="px-3 py-2 bg-[#1E4D2B] hover:bg-[#14371E] font-semibold text-white rounded transition-colors"
              >
                Execute Split Settlement
              </button>
              <button
                onClick={() => handleStepTransition("Refunded")}
                className="px-3 py-2 bg-stone-100 hover:bg-stone-200 border border-[#D1D9D1] font-semibold text-stone-800 rounded transition-colors"
              >
                Refund Trade
              </button>
            </div>
          </div>

          {/* Evidence Uploader Dropzone */}
          <EvidenceUploader escrowId={sampleTrade.tradeId} />
        </main>
      </div>
    </div>
  );
}
