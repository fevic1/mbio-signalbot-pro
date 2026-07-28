const news = [
  "Fed minutes due in 45 minutes.",
  "BTC ETF inflows remain positive for 8 consecutive sessions.",
  "Hyperliquid perpetual volume reaches new weekly high.",
  "Ethereum staking participation climbs above 31%.",
];

export default function NewsTicker() {
  return (
    <div className="absolute bottom-8 left-0 right-16 z-20 h-8 overflow-hidden border-t border-white/10 bg-[#081018]/95 backdrop-blur">
      <div className="flex h-full items-center gap-10 whitespace-nowrap px-4 text-[11px] text-white/70">
        {news.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </div>
  );
}
