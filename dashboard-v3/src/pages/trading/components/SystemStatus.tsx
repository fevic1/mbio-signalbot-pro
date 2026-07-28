const status = [
  ["Exchange", "Connected", "text-green-400"],
  ["WebSocket", "Healthy", "text-green-400"],
  ["Latency", "14 ms", "text-cyan-400"],
  ["Orders", "Ready", "text-green-400"],
];

export default function SystemStatus() {
  return (
    <div className="absolute right-20 top-72 z-30 w-56 rounded-lg border border-white/10 bg-[#0b0f17]/95 p-3 backdrop-blur">
      <div className="mb-3 text-xs font-semibold text-white">
        System Status
      </div>

      <div className="space-y-2">
        {status.map(([label, value, color]) => (
          <div key={label} className="flex items-center justify-between text-[11px]">
            <span className="text-white/50">{label}</span>
            <span className={color}>{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
