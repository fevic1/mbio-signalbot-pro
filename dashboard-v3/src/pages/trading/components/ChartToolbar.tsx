import {
  Crosshair,
  RefreshCw,
  Maximize2,
  Settings2,
  Camera,
  Ruler,
  Magnet,
  Pencil,
} from "lucide-react";

const leftTools = [
  Crosshair,
  Pencil,
  Ruler,
  Magnet,
];

const rightTools = [
  RefreshCw,
  Camera,
  Maximize2,
  Settings2,
];

export default function ChartToolbar() {
  return (
    <div className="flex h-11 items-center justify-between border-b border-white/10 bg-[#0f1118] px-3">
      <div className="flex items-center gap-1">
        {leftTools.map((Icon, i) => (
          <button
            key={i}
            className="flex h-8 w-8 items-center justify-center rounded-md text-white/50 transition hover:bg-white/5 hover:text-cyan-400"
          >
            <Icon className="h-4 w-4" />
          </button>
        ))}

        <div className="mx-2 h-5 w-px bg-white/10" />

        <button className="rounded bg-cyan-500/20 px-2 py-1 text-xs font-medium text-cyan-400">
          Indicators
        </button>

        <button className="rounded px-2 py-1 text-xs text-white/60 hover:bg-white/5">
          Compare
        </button>

        <button className="rounded px-2 py-1 text-xs text-white/60 hover:bg-white/5">
          Templates
        </button>
      </div>

      <div className="flex items-center gap-1">
        {rightTools.map((Icon, i) => (
          <button
            key={i}
            className="flex h-8 w-8 items-center justify-center rounded-md text-white/50 transition hover:bg-white/5 hover:text-cyan-400"
          >
            <Icon className="h-4 w-4" />
          </button>
        ))}
      </div>
    </div>
  );
}
