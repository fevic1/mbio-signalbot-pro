const zones = [
  {
    top: "27%",
    left: "53%",
    width: "9%",
    height: "12%",
  },
  {
    top: "64%",
    left: "30%",
    width: "8%",
    height: "11%",
  },
];

export default function RepricingOverlay() {
  return (
    <>
      {zones.map((zone, index) => (
        <div
          key={index}
          className="pointer-events-none absolute rounded border border-sky-400/60 bg-sky-500/10"
          style={{
            top: zone.top,
            left: zone.left,
            width: zone.width,
            height: zone.height,
          }}
        >
          <div className="absolute inset-0 flex items-center justify-center text-[9px] font-semibold text-sky-300">
            Repricing
          </div>
        </div>
      ))}
    </>
  );
}
