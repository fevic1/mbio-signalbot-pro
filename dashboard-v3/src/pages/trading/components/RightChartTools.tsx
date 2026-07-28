import {
  ZoomIn,
  ZoomOut,
  Move,
  ScanSearch,
  Lock,
  Eye,
} from "lucide-react";

const tools = [
  ZoomIn,
  ZoomOut,
  Move,
  ScanSearch,
  Lock,
  Eye,
];

export default function RightChartTools() {
  return (
    <aside className="absolute right-3 top-3 z-30 flex flex-col gap-2">
      {tools.map((Icon, index) => (
        <button
          key={index}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-[#0b0f17]/95 text-white/50 transition hover:bg-white/5 hover:text-cyan-400"
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </aside>
  );
}
