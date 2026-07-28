const zones = [
  {
    left: "26%",
    top: "64%",
    label: "Accumulation",
  },
  {
    left: "43%",
    top: "48%",
    label: "Manipulation",
  },
  {
    left: "61%",
    top: "26%",
    label: "Expansion",
  },
];

export default function MarketMakerBuyModelOverlay() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className="pointer-events-none absolute rounded border border-emerald-400/60 bg-emerald-500/10 px-2 py-1"
          style={{
            left: zone.left,
            top: zone.top,
          }}
        >
          <span className="text-[9px] font-semibold text-emerald-300">
            {zone.label}
          </span>
        </div>
      ))}
    </>
  );
}
