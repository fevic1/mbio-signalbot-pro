const events = [
  {
    time: "09:30",
    event: "US GDP",
    impact: "High",
  },
  {
    time: "11:00",
    event: "Fed Speech",
    impact: "High",
  },
  {
    time: "14:00",
    event: "Crude Oil",
    impact: "Medium",
  },
  {
    time: "Tomorrow",
    event: "CPI",
    impact: "High",
  },
];

export default function MarketCalendar() {
  return (
    <div className="absolute left-4 top-52 z-20 w-64 rounded-xl border border-white/10 bg-[#0b0f17]/95 backdrop-blur">
      <div className="border-b border-white/10 px-4 py-2 text-xs font-semibold text-white">
        Economic Calendar
      </div>

      <div className="divide-y divide-white/5">
        {events.map((item) => (
          <div
            key={item.time + item.event}
            className="flex items-center justify-between px-4 py-3 text-[11px]"
          >
            <div>
              <div className="text-white">{item.event}</div>
              <div className="text-white/40">{item.time}</div>
            </div>

            <span
              className={`rounded px-2 py-1 text-[10px] ${
                item.impact === "High"
                  ? "bg-red-500/20 text-red-400"
                  : "bg-yellow-500/20 text-yellow-400"
              }`}
            >
              {item.impact}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
