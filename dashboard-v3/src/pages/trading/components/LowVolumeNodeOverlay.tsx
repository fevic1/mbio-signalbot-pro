const gaps = [
  {
    top: "33%",
    height: "7%",
  },
  {
    top: "60%",
    height: "6%",
  },
];

export default function LowVolumeNodeOverlay() {
  return (
    <>
      {gaps.map((gap, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16 border border-dashed border-red-400/40 bg-red-500/5"
          style={{
            top: gap.top,
            height: gap.height,
          }}
        >
          <div className="absolute right-2 top-1 text-[9px] text-red-300">
            LVN
          </div>
        </div>
      ))}
    </>
  );
}
