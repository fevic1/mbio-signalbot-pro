const gaps = [
  {
    top: "24%",
    left: "46%",
    width: "14%",
    height: "7%",
  },
  {
    top: "58%",
    left: "22%",
    width: "11%",
    height: "6%",
  },
];

export default function FairValueGapOverlay() {
  return (
    <>
      {gaps.map((gap, index) => (
        <div
          key={index}
          className="pointer-events-none absolute border border-orange-400/60 bg-orange-400/10"
          style={{
            top: gap.top,
            left: gap.left,
            width: gap.width,
            height: gap.height,
          }}
        >
          <div className="absolute left-1 top-1 text-[9px] font-medium text-orange-300">
            FVG
          </div>
        </div>
      ))}
    </>
  );
}
