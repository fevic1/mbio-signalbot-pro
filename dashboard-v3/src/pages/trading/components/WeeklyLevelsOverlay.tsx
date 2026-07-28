const levels = [
  {
    top: "6%",
    label: "Weekly High",
  },
  {
    top: "93%",
    label: "Weekly Low",
  },
];

export default function WeeklyLevelsOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-fuchsia-400/60"
          style={{ top: level.top }}
        >
          <span className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-fuchsia-300">
            {level.label}
          </span>
        </div>
      ))}
    </>
  );
}
