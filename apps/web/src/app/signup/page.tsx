"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";

export default function SignupPage() {
  const router = useRouter();
  const [role, setRole] = useState<"farmer" | "buyer">("farmer");
  const [businessName, setBusinessName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("North Rift Grain Belt");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!businessName || !email || !phone) {
      alert("Please fill in all required fields.");
      return;
    }
    setSubmitted(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#FAF9F5] flex flex-col justify-between">
      <Navbar />

      <main className="max-w-2xl mx-auto px-6 py-12 flex-1 w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-stone-900 tracking-tight">
            Create Your Account
          </h1>
          <p className="text-sm text-stone-600 mt-2">
            Select your trading role to set up your profile and trade agreements.
          </p>
        </div>

        {submitted ? (
          <div className="bg-white border border-[#D1D9D1] p-8 rounded text-center">
            <div className="w-12 h-12 bg-[#EBF3EC] text-[#1E4D2B] rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-xl">
              ✓
            </div>
            <h2 className="text-xl font-bold text-stone-900 mb-2">Account Initialized</h2>
            <p className="text-sm text-stone-600">
              Welcome, {businessName}. Redirecting to your trade dashboard...
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 2-Role Selection Grid ONLY */}
            <div>
              <label className="block text-xs font-semibold text-stone-700 uppercase tracking-wider mb-2">
                1. Select Trading Role
              </label>
              <div className="grid grid-cols-2 gap-4">
                {/* Farmer Option */}
                <button
                  type="button"
                  onClick={() => setRole("farmer")}
                  className={`p-5 rounded text-left border transition-all ${
                    role === "farmer"
                      ? "border-[#1E4D2B] bg-[#EBF3EC] ring-1 ring-[#1E4D2B]"
                      : "border-[#D1D9D1] bg-white hover:border-stone-400"
                  }`}
                >
                  <div className="text-lg font-bold text-stone-900 mb-1">
                    Farmer / Seller
                  </div>
                  <div className="text-xs text-stone-600">
                    Agricultural Producer
                  </div>
                </button>

                {/* Buyer Option */}
                <button
                  type="button"
                  onClick={() => setRole("buyer")}
                  className={`p-5 rounded text-left border transition-all ${
                    role === "buyer"
                      ? "border-[#1E4D2B] bg-[#EBF3EC] ring-1 ring-[#1E4D2B]"
                      : "border-[#D1D9D1] bg-white hover:border-stone-400"
                  }`}
                >
                  <div className="text-lg font-bold text-stone-900 mb-1">
                    Buyer / Importer
                  </div>
                  <div className="text-xs text-stone-600">
                    Commodity Processor
                  </div>
                </button>
              </div>
            </div>

            {/* Profile Inputs */}
            <div className="bg-white border border-[#D1D9D1] p-6 rounded space-y-4">
              <label className="block text-xs font-semibold text-stone-700 uppercase tracking-wider">
                2. Business Profile Information
              </label>

              <div>
                <label className="block text-xs font-medium text-stone-700 mb-1">
                  Full Name or Business Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Kiprono Cooperative or Apex Millers Ltd"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-[#D1D9D1] rounded bg-stone-50 text-stone-900 text-sm focus:outline-none focus:border-[#1E4D2B] focus:bg-white"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-stone-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="contact@business.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3.5 py-2.5 border border-[#D1D9D1] rounded bg-stone-50 text-stone-900 text-sm focus:outline-none focus:border-[#1E4D2B] focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-stone-700 mb-1">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="+254 700 000 000"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-3.5 py-2.5 border border-[#D1D9D1] rounded bg-stone-50 text-stone-900 text-sm focus:outline-none focus:border-[#1E4D2B] focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-stone-700 mb-1">
                  Farm or Business Location *
                </label>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-[#D1D9D1] rounded bg-stone-50 text-stone-900 text-sm focus:outline-none focus:border-[#1E4D2B] focus:bg-white"
                >
                  <option value="North Rift Grain Belt">North Rift Grain Belt (Uasin Gishu / Trans Nzoia)</option>
                  <option value="Western Agricultural Zone">Western Agricultural Zone (Kakamega / Bungoma)</option>
                  <option value="Central Highlands">Central Highlands (Meru / Nakuru)</option>
                  <option value="Eastern Lowlands">Eastern Lowlands (Machakos / Makueni)</option>
                  <option value="Mombasa Coastal Freight Hub">Mombasa Port & Coastal Hub</option>
                  <option value="Nairobi Commercial Milling District">Nairobi Industrial & Milling District</option>
                  <option value="International Cross-Border Trade">Cross-Border Regional Terminal</option>
                </select>
              </div>
            </div>

            {/* Action Buttons */}
            <div>
              <button
                type="submit"
                className="w-full bg-[#1E4D2B] hover:bg-[#14371E] text-white font-semibold text-base py-3 rounded transition-colors"
              >
                Submit & Create Account
              </button>
            </div>

            <div className="text-center text-xs text-stone-500">
              Already have an active registration?{" "}
              <Link href="/dashboard" className="text-[#1E4D2B] font-semibold underline">
                Go straight to Dashboard
              </Link>
            </div>
          </form>
        )}
      </main>

      <footer className="w-full border-t border-[#D1D9D1] bg-white py-6">
        <div className="max-w-2xl mx-auto px-6 text-center text-xs text-stone-500">
          AgriResolve Protocol · Verified Agricultural Commerce
        </div>
      </footer>
    </div>
  );
}
