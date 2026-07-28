const sweeps = [
  {
    top: "18%",
    label: "Buy-side Sweep",
    color: "text-red-400",
  },
  {
    top: "73%",
    label: "Sell-side Sweep",
    color: "text-green-400",
  },
];

export default function LiquiditySweepOverlay() {
  return (
    <>
      {sweeps.map((sweep) => (
        <div
          key={sweep.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: sweep.top }}
        >
          <div className="border-t border-dotted border-white/40" />

          <div className={`absolute left-3 -top-4 text-[10px] ${sweep.color}`}>
            {sweep.label}
          </div>
        </div>
      ))}
    </>
  );
}
