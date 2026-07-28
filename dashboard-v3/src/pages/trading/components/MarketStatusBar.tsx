const metrics = [
  { label: "Mark", value: "$118,462.30", color: "text-white" },
  { label: "Index", value: "$118,454.80", color: "text-white/80" },
  { label: "24H", value: "+3.42%", color: "text-green-400" },
  { label: "Funding", value: "0.0100%", color: "text-cyan-400" },
  { label: "OI", value: "$7.84B", color: "text-white" },
  { label: "Volume", value: "$2.91B", color: "text-white" },
];

export default function MarketStatusBar() {
  return (
    <div className="flex h-10 items-center gap-6 border-b border-white/10 bg-black px-4 text-xs">
      {metrics.map((item) => (
        <div key={item.label} className="flex items-center gap-2 whitespace-nowrap">
          <span className="text-white/40">{item.label}</span>
          <span className={`font-medium ${item.color}`}>{item.value}</span>
        </div>
      ))}
    </div>
  );
}
