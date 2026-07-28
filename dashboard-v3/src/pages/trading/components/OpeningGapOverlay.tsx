const gaps = [
  {
    top: "31%",
    left: "48%",
    width: "9%",
    height: "5%",
    label: "Opening Gap",
  },
  {
    top: "58%",
    left: "67%",
    width: "8%",
    height: "4%",
    label: "Gap Fill",
  },
];

export default function OpeningGapOverlay() {
  return (
    <>
      {gaps.map((gap) => (
        <div
          key={gap.label + gap.top}
          className="pointer-events-none absolute rounded border border-pink-400/60 bg-pink-500/10"
          style={{
            top: gap.top,
            left: gap.left,
            width: gap.width,
            height: gap.height,
          }}
        >
          <div className="absolute left-1 top-1 text-[9px] text-pink-300">
            {gap.label}
          </div>
        </div>
      ))}
    </>
  );
}
