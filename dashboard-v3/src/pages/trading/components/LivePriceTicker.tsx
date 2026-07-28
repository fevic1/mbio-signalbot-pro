const quotes = [
  { symbol: "BTC", price: "118,462.30", change: "+3.42%" },
  { symbol: "ETH", price: "6,842.55", change: "+2.18%" },
  { symbol: "SOL", price: "412.71", change: "+5.63%" },
  { symbol: "XRP", price: "4.1832", change: "-0.72%" },
  { symbol: "BNB", price: "1,204.61", change: "+1.04%" },
];

export default function LivePriceTicker() {
  return (
    <div className="absolute left-0 right-16 top-0 z-20 h-8 overflow-hidden border-b border-white/10 bg-[#081018]/90 backdrop-blur">
      <div className="flex h-full items-center gap-8 whitespace-nowrap px-4 text-[11px]">
        {quotes.map((quote) => (
          <div key={quote.symbol} className="flex items-center gap-2">
            <span className="font-semibold text-white">
              {quote.symbol}
            </span>

            <span className="text-white/70">
              {quote.price}
            </span>

            <span
              className={
                quote.change.startsWith("-")
                  ? "text-red-400"
                  : "text-green-400"
              }
            >
              {quote.change}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
