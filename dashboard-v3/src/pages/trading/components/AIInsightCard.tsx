export default function AIInsightCard() {
  return (
    <div className="absolute left-72 bottom-52 z-20 w-80 rounded-xl border border-cyan-500/20 bg-[#07131d]/95 p-4 backdrop-blur">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-cyan-400">
          AI Market Insight
        </span>

        <span className="rounded bg-cyan-500/20 px-2 py-1 text-[10px] text-cyan-300">
          Confidence 84%
        </span>
      </div>

      <p className="mt-3 text-xs leading-6 text-white/70">
        Momentum remains positive above intraday VWAP while liquidity is
        concentrated near recent highs. Watch for continuation only after a
        confirmed breakout with sustained volume.
      </p>
    </div>
  );
}
