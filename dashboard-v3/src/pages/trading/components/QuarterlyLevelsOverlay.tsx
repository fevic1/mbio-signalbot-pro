const quarters = [
  {
    top: "25%",
    label: "Q1",
  },
  {
    top: "50%",
    label: "Q2",
  },
  {
    top: "75%",
    label: "Q3",
  },
];

export default function QuarterlyLevelsOverlay() {
  return (
    <>
      {quarters.map((quarter) => (
        <div
          key={quarter.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-sky-400/30"
          style={{ top: quarter.top }}
        >
          <span className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-sky-300">
            {quarter.label}
          </span>
        </div>
      ))}
    </>
  );
}
