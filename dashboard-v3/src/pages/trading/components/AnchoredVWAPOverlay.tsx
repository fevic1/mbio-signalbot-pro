const lines = [
  {
    top: "29%",
    label: "Daily AVWAP",
  },
  {
    top: "61%",
    label: "Weekly AVWAP",
  },
];

export default function AnchoredVWAPOverlay() {
  return (
    <>
      {lines.map((line) => (
        <div
          key={line.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-cyan-300/40"
          style={{ top: line.top }}
        >
          <span className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-cyan-300">
            {line.label}
          </span>
        </div>
      ))}
    </>
  );
}
