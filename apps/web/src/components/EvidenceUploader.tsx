"use client";

import React, { useState } from "react";

interface UploadedEvidence {
  name: string;
  size: number;
  type: string;
  hash: string;
  timestamp: string;
  status: "hashed" | "submitted" | "investigated";
}

interface EvidenceUploaderProps {
  escrowId: string | number;
  onEvidenceProcessed?: (evidence: UploadedEvidence) => void;
}

export default function EvidenceUploader({
  escrowId,
  onEvidenceProcessed,
}: EvidenceUploaderProps) {
  const [evidenceList, setEvidenceList] = useState<UploadedEvidence[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [evidenceType, setEvidenceType] = useState("Weighbridge Slip");

  const computeFileSha256 = async (file: File): Promise<string> => {
    const arrayBuffer = await file.arrayBuffer();
    const digestBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
    const hashArray = Array.from(new Uint8Array(digestBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsProcessing(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const hash = await computeFileSha256(file);

        const newEvidence: UploadedEvidence = {
          name: file.name,
          size: file.size,
          type: evidenceType,
          hash,
          timestamp: new Date().toLocaleTimeString(),
          status: "hashed",
        };

        // Try submitting to indexer endpoint if available
        const indexerUrl = process.env.NEXT_PUBLIC_INDEXER_API_URL || "http://localhost:8000";
        try {
          await fetch(`${indexerUrl}/api/disputes/${escrowId}/investigate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              terms: {
                totalAmount: "10000000000",
                contractQuantityKg: 10000,
                baseMoistureBps: 1200,
              },
              inspection: {
                deliveredQuantityKg: 9800,
                actualMoistureBps: 1350,
                weighbridgeTicketId: file.name,
              },
              evidenceList: [
                {
                  evidenceType,
                  sourceUri: `local://${file.name}`,
                  hash,
                  contentSummary: `Uploaded audit dossier: ${file.name} (${file.size} bytes)`,
                },
              ],
            }),
          });
          newEvidence.status = "investigated";
        } catch {
          newEvidence.status = "hashed";
        }

        setEvidenceList((prev) => [newEvidence, ...prev]);
        if (onEvidenceProcessed) onEvidenceProcessed(newEvidence);
      }
    } catch (err: any) {
      alert(`Error computing cryptographic digest: ${err.message}`);
    } finally {
      setIsProcessing(false);
      e.target.value = "";
    }
  };

  return (
    <div className="bg-white border border-[#D1D9D1] p-6 rounded space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-stone-900">
            Cryptographic Evidence Uploader
          </h3>
          <p className="text-xs text-stone-600 mt-0.5">
            Upload weighbridge tickets, moisture sensor logs, or phytosanitary certificates for automated audit.
          </p>
        </div>

        <div>
          <select
            value={evidenceType}
            onChange={(e) => setEvidenceType(e.target.value)}
            className="px-2.5 py-1.5 border border-[#D1D9D1] rounded bg-stone-50 text-xs font-medium text-stone-800"
          >
            <option value="Weighbridge Slip">Weighbridge Slip</option>
            <option value="Moisture Lab Analysis">Moisture Lab Analysis</option>
            <option value="Bill of Lading">Bill of Lading / Transport Waybill</option>
            <option value="Inspection Certificate">Phytosanitary Certificate</option>
          </select>
        </div>
      </div>

      {/* Flat Rectangular 2px Dashed Dropzone */}
      <div className="relative border-2 border-dashed border-stone-300 bg-stone-50 hover:bg-stone-100 transition-colors p-8 rounded text-center cursor-pointer">
        <input
          type="file"
          multiple
          onChange={handleFileUpload}
          disabled={isProcessing}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="space-y-1">
          <div className="text-sm font-semibold text-stone-800">
            {isProcessing ? "Computing SHA-256 Digest..." : "Click or drag documents to upload"}
          </div>
          <div className="text-xs text-stone-500">
            PDF, PNG, CSV, or TXT up to 25MB · Deterministic SHA-256 computed locally
          </div>
        </div>
      </div>

      {/* Uploaded Evidence Dossier List */}
      {evidenceList.length > 0 && (
        <div className="border border-[#D1D9D1] rounded divide-y divide-[#D1D9D1] text-xs">
          {evidenceList.map((item, idx) => (
            <div key={idx} className="p-3 flex items-center justify-between bg-stone-50">
              <div className="space-y-1">
                <div className="font-medium text-stone-900 flex items-center space-x-2">
                  <span>{item.name}</span>
                  <span className="px-1.5 py-0.5 bg-stone-200 text-stone-700 rounded text-[10px]">
                    {item.type}
                  </span>
                </div>
                <div className="font-mono text-[11px] text-stone-500">
                  SHA-256: {item.hash.substring(0, 16)}...{item.hash.substring(item.hash.length - 16)}
                </div>
              </div>

              <div className="text-right">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#EBF3EC] text-[#1E4D2B]">
                  {item.status.toUpperCase()}
                </span>
                <div className="text-[10px] text-stone-400 mt-1">{item.timestamp}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
