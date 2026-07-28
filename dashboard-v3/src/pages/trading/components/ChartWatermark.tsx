export default function ChartWatermark() {
  return (
    <div className="pointer-events-none absolute left-8 bottom-8 z-10 select-none">
      <div className="text-5xl font-bold tracking-tight text-white/5">
        BTCUSDT
      </div>

      <div className="mt-1 text-lg font-medium tracking-widest text-cyan-400/20">
        HYPERLIQUID
      </div>

      <div className="mt-2 text-xs uppercase tracking-[0.35em] text-white/10">
        Institutional Trading Workspace
      </div>
    </div>
  );
}
