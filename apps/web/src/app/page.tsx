import Link from "next/link";
import Navbar from "@/components/Navbar";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#FAF9F5] flex flex-col justify-between">
      <Navbar />

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-[#EBF3EC] border border-[#D1D9D1] rounded-full text-xs font-semibold text-[#1E4D2B] mb-8">
          <span>Agricultural Trade Escrow & Resolution</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-stone-900 tracking-tight leading-tight max-w-4xl mx-auto mb-6">
          Fair Trade, Zero Disputes. Secure your farm deals and resolve disagreements without the stress.
        </h1>

        <p className="text-lg sm:text-xl text-stone-600 max-w-3xl mx-auto mb-10 leading-relaxed">
          AgriResolve keeps your money safe in secure holding until the produce is delivered. If something goes wrong, our system helps you settle it quickly using actual proof.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/signup"
            className="w-full sm:w-auto bg-[#1E4D2B] hover:bg-[#14371E] text-white font-semibold text-base px-8 py-3.5 rounded transition-colors"
          >
            Start a Secure Deal
          </Link>
          <Link
            href="/dashboard"
            className="w-full sm:w-auto bg-white border border-[#D1D9D1] hover:border-stone-400 text-stone-800 font-semibold text-base px-8 py-3.5 rounded transition-colors"
          >
            View Live Deals
          </Link>
        </div>

        {/* 3-Step Walkthrough */}
        <section id="how-it-works" className="mt-28 text-left">
          <div className="border-b border-[#D1D9D1] pb-4 mb-10">
            <h2 className="text-2xl font-bold text-stone-900">How It Works</h2>
            <p className="text-sm text-stone-600 mt-1">Simple, predictable agricultural trade in three steps.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1 */}
            <div className="bg-white border border-[#D1D9D1] p-6 rounded">
              <div className="w-10 h-10 bg-[#EBF3EC] text-[#1E4D2B] font-bold text-lg rounded flex items-center justify-center mb-4">
                1
              </div>
              <h3 className="text-lg font-bold text-stone-900 mb-2">Create & Fund</h3>
              <p className="text-sm text-stone-600 leading-relaxed">
                The buyer puts money into secure holding.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white border border-[#D1D9D1] p-6 rounded">
              <div className="w-10 h-10 bg-[#EBF3EC] text-[#1E4D2B] font-bold text-lg rounded flex items-center justify-center mb-4">
                2
              </div>
              <h3 className="text-lg font-bold text-stone-900 mb-2">Deliver & Confirm</h3>
              <p className="text-sm text-stone-600 leading-relaxed">
                The farmer sends the produce.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white border border-[#D1D9D1] p-6 rounded">
              <div className="w-10 h-10 bg-[#EBF3EC] text-[#1E4D2B] font-bold text-lg rounded flex items-center justify-center mb-4">
                3
              </div>
              <h3 className="text-lg font-bold text-stone-900 mb-2">Smooth Payday</h3>
              <p className="text-sm text-stone-600 leading-relaxed">
                Once confirmed, the money is released instantly. If there is a dispute, simply upload your delivery records and invoices, and AgriResolve will help split the funds fairly.
              </p>
            </div>
          </div>
        </section>

        {/* Guarantees Section */}
        <section id="guarantees" className="mt-20 text-left bg-white border border-[#D1D9D1] p-8 rounded">
          <h2 className="text-xl font-bold text-stone-900 mb-4">Our Guarantees to Farmers & Buyers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-stone-600">
            <div>
              <h4 className="font-semibold text-stone-900 mb-1">Guaranteed Delivery Protection</h4>
              <p>Funds remain locked until physical delivery is inspected and confirmed. Farmers know the money is already committed before loading trucks.</p>
            </div>
            <div>
              <h4 className="font-semibold text-stone-900 mb-1">Objective Quality Calculations</h4>
              <p>Moisture shrinkage and weight variations follow verified regional grain standards rather than arbitrary deductions.</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-[#D1D9D1] bg-white py-8">
        <div className="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-500">
          <div>© 2026 AgriResolve Protocol. Built for reliable agricultural commerce.</div>
          <div className="flex space-x-6 mt-4 sm:mt-0 font-medium">
            <Link href="/signup" className="hover:text-stone-900">Sign Up</Link>
            <Link href="/dashboard" className="hover:text-stone-900">Dashboard</Link>
            <Link href="#how-it-works" className="hover:text-stone-900">How It Works</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
