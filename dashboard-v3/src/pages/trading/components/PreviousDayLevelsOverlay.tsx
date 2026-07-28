const levels = [
  {
    top: "11%",
    label: "PDH",
    color: "border-red-400",
  },
  {
    top: "48%",
    label: "PDO",
    color: "border-cyan-400",
  },
  {
    top: "84%",
    label: "PDL",
    color: "border-green-400",
  },
];

export default function PreviousDayLevelsOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className={`pointer-events-none absolute left-12 right-16 border-t border-dashed ${level.color}/70`}
          style={{ top: level.top }}
        >
          <span className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-white/70">
            {level.label}
          </span>
        </div>
      ))}
    </>
  );
}
