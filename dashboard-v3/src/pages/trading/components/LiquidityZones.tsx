const zones = [
  {
    top: "18%",
    height: "9%",
    color: "bg-red-500/10 border-red-500/30",
    label: "Sell Liquidity",
  },
  {
    top: "62%",
    height: "10%",
    color: "bg-green-500/10 border-green-500/30",
    label: "Buy Liquidity",
  },
];

export default function LiquidityZones() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className={`pointer-events-none absolute left-12 right-16 z-10 border ${zone.color}`}
          style={{
            top: zone.top,
            height: zone.height,
          }}
        >
          <div className="absolute left-2 top-1 text-[10px] font-medium text-white/60">
            {zone.label}
          </div>
        </div>
      ))}
    </>
  );
}
