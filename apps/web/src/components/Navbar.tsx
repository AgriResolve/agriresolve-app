import Link from "next/link";

export default function Navbar() {
  return (
    <header className="w-full bg-[#FAF9F5] border-b border-[#D1D9D1] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-[#1E4D2B] flex items-center justify-center rounded text-white font-bold text-lg">
            A
          </div>
          <span className="font-bold text-xl tracking-tight text-stone-900">
            AgriResolve
          </span>
        </Link>

        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-stone-700">
          <Link href="#how-it-works" className="hover:text-stone-900 transition-colors">
            How It Works
          </Link>
          <Link href="#guarantees" className="hover:text-stone-900 transition-colors">
            Guarantees
          </Link>
          <Link href="/dashboard" className="hover:text-stone-900 transition-colors">
            Trade Dashboard
          </Link>
        </nav>

        <div className="flex items-center space-x-4">
          <Link
            href="/signup"
            className="text-sm font-semibold text-stone-700 hover:text-stone-900 px-3 py-2"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="bg-[#1E4D2B] hover:bg-[#14371E] text-white text-sm font-medium px-4 py-2 rounded transition-colors"
          >
            Start a Secure Deal
          </Link>
        </div>
      </div>
    </header>
  );
}
