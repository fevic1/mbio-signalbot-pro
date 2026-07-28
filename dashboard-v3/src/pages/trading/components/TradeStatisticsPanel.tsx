const stats = [
  ["Win Rate", "72.4%", "text-green-400"],
  ["Trades", "184", "text-white"],
  ["PnL Today", "+$4,284", "text-green-400"],
  ["Sharpe", "2.31", "text-cyan-400"],
  ["Max DD", "4.1%", "text-yellow-400"],
  ["Exposure", "$182K", "text-white"],
];

export default function TradeStatisticsPanel() {
  return (
    <div className="absolute right-20 bottom-56 z-20 w-60 rounded-xl border border-white/10 bg-[#0b0f17]/95 p-4 backdrop-blur">
      <div className="mb-3 text-xs font-semibold text-white">
        Strategy Statistics
      </div>

      <div className="space-y-2">
        {stats.map(([label, value, color]) => (
          <div
            key={label}
            className="flex items-center justify-between text-[11px]"
          >
            <span className="text-white/45">{label}</span>
            <span className={color}>{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
