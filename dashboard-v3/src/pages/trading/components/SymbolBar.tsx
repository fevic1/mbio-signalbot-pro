import { Search } from "lucide-react";

const symbols = [
  "BTCUSDT",
  "ETHUSDT",
  "SOLUSDT",
  "XRPUSDT",
  "BNBUSDT",
];

export default function SymbolBar() {
  return (
    <div className="flex h-12 items-center gap-3 border-b border-white/10 bg-gray-950 px-4">
      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5">
        <Search className="h-4 w-4 text-white/40" />

        <input
          placeholder="Search symbol..."
          className="w-40 bg-transparent text-sm text-white outline-none placeholder:text-white/30"
        />
      </div>

      <div className="flex gap-2 overflow-x-auto">
        {symbols.map((symbol, index) => (
          <button
            key={symbol}
            className={`rounded-md px-3 py-1.5 text-sm transition ${
              index === 0
                ? "bg-cyan-500 text-black"
                : "bg-white/5 text-white/70 hover:bg-white/10"
            }`}
          >
            {symbol}
          </button>
        ))}
      </div>
    </div>
  );
}
