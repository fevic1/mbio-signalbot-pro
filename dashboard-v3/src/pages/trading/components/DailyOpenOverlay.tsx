const opens = [
  {
    top: "46%",
    label: "Daily Open",
    color: "border-cyan-400",
  },
  {
    top: "54%",
    label: "NY Open",
    color: "border-yellow-400",
  },
  {
    top: "63%",
    label: "London Open",
    color: "border-green-400",
  },
];

export default function DailyOpenOverlay() {
  return (
    <>
      {opens.map((line) => (
        <div
          key={line.label}
          className={`pointer-events-none absolute left-12 right-16 border-t border-dashed ${line.color}/60`}
          style={{ top: line.top }}
        >
          <span className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-white/70">
            {line.label}
          </span>
        </div>
      ))}
    </>
  );
}
