"use client";

import React from "react";

export interface TradeSummary {
  tradeId: string;
  buyerAddress: string;
  farmerAddress: string;
  amount: string;
  tokenSymbol: string;
  commodityGrade: string;
  contractQuantity: string;
  expiryDate: string;
}

interface TradeDetailsPanelProps {
  trade: TradeSummary;
}

export default function TradeDetailsPanel({ trade }: TradeDetailsPanelProps) {
  return (
    <div className="bg-white border border-[#D1D9D1] rounded p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-[#D1D9D1] pb-3">
        <div>
          <h3 className="text-base font-bold text-stone-900">Trade Agreement Dossier</h3>
          <p className="text-xs text-stone-500">Verified On-Chain Custody Records</p>
        </div>
        <div className="font-mono text-xs font-bold px-2.5 py-1 bg-[#EBF3EC] text-[#1E4D2B] rounded">
          TRADE #{trade.tradeId}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="space-y-1">
          <span className="text-stone-500">Buyer / Depositor Account:</span>
          <div className="font-mono font-medium text-stone-900 bg-stone-50 p-2 rounded border border-[#D1D9D1] break-all">
            {trade.buyerAddress}
          </div>
        </div>

        <div className="space-y-1">
          <span className="text-stone-500">Farmer / Beneficiary Account:</span>
          <div className="font-mono font-medium text-stone-900 bg-stone-50 p-2 rounded border border-[#D1D9D1] break-all">
            {trade.farmerAddress}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
        <div className="p-3 bg-stone-50 border border-[#D1D9D1] rounded">
          <span className="text-stone-500 block">Locked Escrow</span>
          <span className="text-sm font-bold text-stone-900 font-mono mt-0.5 block">
            {trade.amount} {trade.tokenSymbol}
          </span>
        </div>

        <div className="p-3 bg-stone-50 border border-[#D1D9D1] rounded">
          <span className="text-stone-500 block">Contracted Quantity</span>
          <span className="text-sm font-bold text-stone-900 font-mono mt-0.5 block">
            {trade.contractQuantity}
          </span>
        </div>

        <div className="p-3 bg-stone-50 border border-[#D1D9D1] rounded">
          <span className="text-stone-500 block">Commodity Spec</span>
          <span className="text-sm font-bold text-stone-900 mt-0.5 block">
            {trade.commodityGrade}
          </span>
        </div>

        <div className="p-3 bg-stone-50 border border-[#D1D9D1] rounded">
          <span className="text-stone-500 block">Expiry Window</span>
          <span className="text-sm font-bold text-stone-900 font-mono mt-0.5 block">
            {trade.expiryDate}
          </span>
        </div>
      </div>
    </div>
  );
}
