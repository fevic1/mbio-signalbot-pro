const zones = [
  {
    top: "22%",
    height: "16%",
  },
  {
    top: "52%",
    height: "18%",
  },
];

export default function DoubleDistributionOverlay() {
  return (
    <>
      {zones.map((zone, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-14 right-20 rounded border border-cyan-400/50 bg-cyan-500/10"
          style={{
            top: zone.top,
            height: zone.height,
          }}
        >
          <div className="absolute left-2 top-2 text-[9px] text-cyan-300">
            Distribution
          </div>
        </div>
      ))}
    </>
  );
}
