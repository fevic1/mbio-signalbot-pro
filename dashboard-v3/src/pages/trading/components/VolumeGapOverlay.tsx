const gaps = [
  {
    top: "31%",
    height: "8%",
  },
  {
    top: "56%",
    height: "7%",
  },
];

export default function VolumeGapOverlay() {
  return (
    <>
      {gaps.map((gap, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16 rounded border border-orange-300/40 bg-orange-500/10"
          style={{
            top: gap.top,
            height: gap.height,
          }}
        >
          <div className="absolute right-2 top-1 text-[9px] text-orange-300">
            Volume Gap
          </div>
        </div>
      ))}
    </>
  );
}
