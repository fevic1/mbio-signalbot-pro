import {
  TrendingUp,
  BarChart3,
  Activity,
  Layers3,
} from "lucide-react";

export default function ChartOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-4 top-4 z-20">
        <div className="rounded-lg border border-white/10 bg-[#0b0f17]/95 px-3 py-2 backdrop-blur">
          <div className="text-xs font-semibold text-white">
            BTCUSDT Perpetual
          </div>

          <div className="mt-1 flex gap-3 text-[11px]">
            <span className="text-green-400">O 118,210</span>
            <span className="text-cyan-400">H 118,648</span>
            <span className="text-red-400">L 117,982</span>
            <span className="text-white">C 118,462</span>
          </div>
        </div>
      </div>

      <div className="pointer-events-none absolute left-4 bottom-4 z-20 flex items-center gap-2">
        {[TrendingUp, BarChart3, Activity, Layers3].map((Icon, i) => (
          <div
            key={i}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-[#0b0f17]/90"
          >
            <Icon className="h-4 w-4 text-white/60" />
          </div>
        ))}
      </div>

      <div className="pointer-events-none absolute right-4 bottom-4 z-20 rounded-lg border border-cyan-500/30 bg-[#08111f]/95 px-4 py-2 backdrop-blur">
        <div className="text-[11px] uppercase tracking-wide text-cyan-400">
          Last Price
        </div>

        <div className="mt-1 text-lg font-semibold text-white">
          118,462.30
        </div>

        <div className="text-xs text-green-400">
          +3.42%
        </div>
      </div>
    </>
  );
}
