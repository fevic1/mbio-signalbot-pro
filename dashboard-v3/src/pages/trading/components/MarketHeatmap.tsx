const markets = [
  { symbol: "BTC", value: "+3.42%" },
  { symbol: "ETH", value: "+2.18%" },
  { symbol: "SOL", value: "+5.61%" },
  { symbol: "XRP", value: "-0.71%" },
  { symbol: "BNB", value: "+1.05%" },
  { symbol: "ARB", value: "-1.83%" },
];

export default function MarketHeatmap() {
  return (
    <div className="absolute bottom-12 left-4 z-20 grid grid-cols-3 gap-2">
      {markets.map((market) => (
        <div
          key={market.symbol}
          className={`rounded-lg border px-3 py-2 text-center ${
            market.value.startsWith("-")
              ? "border-red-500/20 bg-red-500/10"
              : "border-green-500/20 bg-green-500/10"
          }`}
        >
          <div className="text-xs font-semibold text-white">
            {market.symbol}
          </div>

          <div
            className={`mt-1 text-[11px] ${
              market.value.startsWith("-")
                ? "text-red-400"
                : "text-green-400"
            }`}
          >
            {market.value}
          </div>
        </div>
      ))}
    </div>
  );
}
