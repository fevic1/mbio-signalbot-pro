import {
  Play,
  Pause,
  Square,
  MoreVertical,
} from "lucide-react";

interface BotCardProps {
  id: string;
  strategy: string;
  symbol: string;
  status: string;
  pnl: string;
}

export default function BotCard({
  id,
  strategy,
  symbol,
  status,
  pnl,
}: BotCardProps) {
  const positive = pnl.startsWith("+");
  const running = status === "RUNNING";

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold text-white">
            {strategy}
          </div>

          <div className="text-xs text-white/50">
            {symbol}
          </div>

          <div className="mt-1 text-[11px] text-white/30">
            {id}
          </div>
        </div>

        <button className="text-white/40 hover:text-white">
          <MoreVertical className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span
          className={`rounded-full px-2 py-1 text-[11px] font-medium ${
            running
              ? "bg-green-500/20 text-green-400"
              : "bg-yellow-500/20 text-yellow-400"
          }`}
        >
          {status}
        </span>

        <span
          className={`text-sm font-semibold ${
            positive ? "text-green-400" : "text-red-400"
          }`}
        >
          {pnl} USDT
        </span>
      </div>

      <div className="mt-4 flex gap-2">
        <button className="flex-1 rounded-md bg-green-600 py-2 text-white hover:bg-green-500">
          <Play className="mx-auto h-4 w-4" />
        </button>

        <button className="flex-1 rounded-md bg-yellow-600 py-2 text-white hover:bg-yellow-500">
          <Pause className="mx-auto h-4 w-4" />
        </button>

        <button className="flex-1 rounded-md bg-red-600 py-2 text-white hover:bg-red-500">
          <Square className="mx-auto h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
