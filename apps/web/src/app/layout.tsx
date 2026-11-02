import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgriResolve | Fair Agricultural Trade Settlement",
  description:
    "Secure agricultural escrow holding, delivery confirmation, and evidence-based dispute resolution.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#FAF9F5] text-stone-900 font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
