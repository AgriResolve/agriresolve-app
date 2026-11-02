"use client";

import React from "react";

export type EscrowStep = "Funded" | "Delivered" | "Disputed" | "Resolved" | "Refunded";

interface EscrowStepperProps {
  currentStep: EscrowStep;
}

const STEPS: EscrowStep[] = ["Funded", "Delivered", "Disputed", "Resolved", "Refunded"];

export default function EscrowStepper({ currentStep }: EscrowStepperProps) {
  const currentIndex = STEPS.indexOf(currentStep);

  return (
    <div className="w-full bg-white border border-[#D1D9D1] p-6 rounded">
      <div className="text-xs font-semibold text-stone-600 uppercase tracking-wider mb-6">
        Escrow Settlement State Machine
      </div>

      <div className="relative flex items-center justify-between">
        {/* Connecting Solid 2px Line */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-[#D1D9D1] -translate-y-1/2 z-0" />

        {/* Highlighted portion of Line */}
        <div
          className="absolute top-1/2 left-0 h-0.5 bg-[#1E4D2B] -translate-y-1/2 z-0 transition-all duration-300"
          style={{
            width: `${Math.max(0, (currentIndex / (STEPS.length - 1)) * 100)}%`,
          }}
        />

        {/* 5 Nodes */}
        {STEPS.map((step, idx) => {
          const isPassed = idx < currentIndex;
          const isCurrent = idx === currentIndex;
          const isPending = idx > currentIndex;

          let badgeColor = "bg-white border-[#D1D9D1] text-stone-400";
          if (isCurrent) {
            badgeColor = "bg-[#1E4D2B] border-[#1E4D2B] text-white";
          } else if (isPassed) {
            badgeColor = "bg-[#2D6A4F] border-[#2D6A4F] text-white";
          }

          return (
            <div key={step} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all ${badgeColor}`}
              >
                {isPassed ? "✓" : idx + 1}
              </div>
              <div className="mt-2 text-xs font-medium text-center">
                <span
                  className={
                    isCurrent
                      ? "text-[#1E4D2B] font-bold"
                      : isPassed
                      ? "text-stone-900"
                      : "text-stone-400"
                  }
                >
                  {step}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
