const stats = [
  {
    label: "Position",
    value: "LONG",
    color: "text-green-400",
  },
  {
    label: "PnL",
    value: "+$482.16",
    color: "text-green-400",
  },
  {
    label: "Leverage",
    value: "10x",
    color: "text-cyan-400",
  },
  {
    label: "Margin",
    value: "$2,500",
    color: "text-white",
  },
];

export default function FloatingTradeStats() {
  return (
    <div className="absolute bottom-5 left-1/2 z-30 -translate-x-1/2">
      <div className="flex items-center gap-6 rounded-xl border border-white/10 bg-[#0b0f17]/95 px-5 py-3 shadow-2xl backdrop-blur-xl">
        {stats.map((item) => (
          <div key={item.label}>
            <div className="text-[10px] uppercase tracking-wider text-white/40">
              {item.label}
            </div>

            <div className={`mt-1 text-sm font-semibold ${item.color}`}>
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
