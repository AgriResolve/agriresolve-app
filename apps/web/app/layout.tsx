import "./globals.css";
import type { Metadata } from "next";
import { Navbar } from "../components/Navbar";

export const metadata: Metadata = {
  title: "AgriResolve | Agricultural Dispute Escrow Protocol on Stellar",
  description:
    "Soroban-powered smart escrow protocol integrating autonomous AI evidence investigation with immutable on-chain financial settlement.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#090d0b] text-zinc-100 flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-emerald-950/40 bg-zinc-950/60 py-6 text-center text-xs text-zinc-500">
          <p>AgriResolve Protocol • Stellar Soroban & Meterless AI • Drips Wave 11</p>
        </footer>
      </body>
    </html>
  );
}
