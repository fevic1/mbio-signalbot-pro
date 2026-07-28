const levels = [
  {
    top: "2%",
    label: "Monthly High",
  },
  {
    top: "97%",
    label: "Monthly Low",
  },
  {
    top: "52%",
    label: "Monthly Open",
  },
];

export default function MonthlyLevelsOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-indigo-400/60"
          style={{ top: level.top }}
        >
          <span className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-indigo-300">
            {level.label}
          </span>
        </div>
      ))}
    </>
  );
}
