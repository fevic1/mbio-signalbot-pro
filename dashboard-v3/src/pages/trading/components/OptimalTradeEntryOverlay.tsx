const zones = [
  {
    top: "42%",
    left: "41%",
    width: "10%",
    height: "6%",
    label: "OTE Long",
  },
  {
    top: "28%",
    left: "63%",
    width: "9%",
    height: "5%",
    label: "OTE Short",
  },
];

export default function OptimalTradeEntryOverlay() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className="pointer-events-none absolute rounded border border-lime-400/60 bg-lime-500/10"
          style={{
            top: zone.top,
            left: zone.left,
            width: zone.width,
            height: zone.height,
          }}
        >
          <div className="absolute inset-0 flex items-center justify-center text-[9px] font-semibold text-lime-300">
            {zone.label}
          </div>
        </div>
      ))}
    </>
  );
}
