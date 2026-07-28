const sessions = [
  { name: "Sydney", active: false },
  { name: "Tokyo", active: true },
  { name: "London", active: false },
  { name: "New York", active: false },
];

export default function MarketSessionBadge() {
  return (
    <div className="absolute left-4 top-12 z-30 flex gap-2">
      {sessions.map((session) => (
        <div
          key={session.name}
          className={`rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-wider ${
            session.active
              ? "border-cyan-400 bg-cyan-500/20 text-cyan-400"
              : "border-white/10 bg-[#0b0f17]/90 text-white/40"
          }`}
        >
          {session.name}
        </div>
      ))}
    </div>
  );
}
