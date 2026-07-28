const timeframes = [
  "1m",
  "3m",
  "5m",
  "15m",
  "30m",
  "1H",
  "4H",
  "1D",
  "1W",
];

export default function TimeframeBar() {
  return (
    <div className="flex h-10 items-center gap-1 border-b border-white/10 bg-gray-950 px-3">
      {timeframes.map((tf, index) => (
        <button
          key={tf}
          className={`rounded-md px-3 py-1 text-xs font-medium transition ${
            index === 5
              ? "bg-cyan-500 text-black"
              : "text-white/60 hover:bg-white/5 hover:text-white"
          }`}
        >
          {tf}
        </button>
      ))}

      <div className="ml-auto flex items-center gap-2 text-xs text-white/40">
        UTC
      </div>
    </div>
  );
}
