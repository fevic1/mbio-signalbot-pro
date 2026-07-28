const zones = [
  {
    left: "22%",
    top: "23%",
    label: "Distribution",
  },
  {
    left: "47%",
    top: "39%",
    label: "Manipulation",
  },
  {
    left: "69%",
    top: "67%",
    label: "Expansion",
  },
];

export default function MarketMakerSellModelOverlay() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className="pointer-events-none absolute rounded border border-red-400/60 bg-red-500/10 px-2 py-1"
          style={{
            left: zone.left,
            top: zone.top,
          }}
        >
          <span className="text-[9px] font-semibold text-red-300">
            {zone.label}
          </span>
        </div>
      ))}
    </>
  );
}
