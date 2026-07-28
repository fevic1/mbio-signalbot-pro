const pools = [
  {
    top: "17%",
    label: "External Liquidity",
  },
  {
    top: "78%",
    label: "Internal Liquidity",
  },
];

export default function LiquidityPoolOverlay() {
  return (
    <>
      {pools.map((pool) => (
        <div
          key={pool.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: pool.top }}
        >
          <div className="border-t border-dashed border-cyan-300/40" />

          <div className="absolute right-3 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-cyan-300">
            {pool.label}
          </div>
        </div>
      ))}
    </>
  );
}
