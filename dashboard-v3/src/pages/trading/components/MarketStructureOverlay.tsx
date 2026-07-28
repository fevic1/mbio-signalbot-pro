const levels = [
  { top: "12%", label: "Resistance", color: "border-red-400" },
  { top: "32%", label: "BOS", color: "border-yellow-400" },
  { top: "51%", label: "EQ", color: "border-cyan-400" },
  { top: "71%", label: "Support", color: "border-green-400" },
];

export default function MarketStructureOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className={`pointer-events-none absolute left-12 right-16 border-t border-dashed ${level.color}`}
          style={{ top: level.top }}
        >
          <span className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[10px] text-white/60">
            {level.label}
          </span>
        </div>
      ))}
    </>
  );
}
