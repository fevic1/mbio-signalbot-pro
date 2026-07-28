import {
  MousePointer2,
  Crosshair,
  TrendingUp,
  Minus,
  Brush,
  Type,
  ArrowUpRight,
  Activity,
  Ruler,
  Magnet,
  Eraser,
  Trash2,
} from "lucide-react";

const tools = [
  MousePointer2,
  Crosshair,
  TrendingUp,
  Minus,
  Brush,
  Type,
  ArrowUpRight,
  Activity,
  Ruler,
  Magnet,
  Eraser,
  Trash2,
];

export default function LeftChartTools() {
  return (
    <aside className="flex w-12 flex-col items-center gap-1 border-r border-white/10 bg-[#0b0f17] py-2">
      {tools.map((Icon, index) => (
        <button
          key={index}
          className="flex h-9 w-9 items-center justify-center rounded-md text-white/50 transition hover:bg-white/5 hover:text-cyan-400"
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </aside>
  );
}
