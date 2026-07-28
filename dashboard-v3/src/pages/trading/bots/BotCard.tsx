import {
  Play,
  Pause,
  Square,
  TrendingUp,
  Settings,
} from "lucide-react";

export interface Bot {
  id: string;
  strategy: string;
  asset: string;
  status: "Running" | "Paused" | "Stopped";
  pnl: string;
  runtime: string;
}

interface BotCardProps {
  bot: Bot;
  onClick?: () => void;
}

export default function BotCard({
  bot,
  onClick,
}: BotCardProps) {
  const statusClass = {
    Running: "bg-green-500/20 text-green-400",
    Paused: "bg-yellow-500/20 text-yellow-400",
    Stopped: "bg-red-500/20 text-red-400",
  }[bot.status];

  const StatusIcon = {
    Running: Play,
    Paused: Pause,
    Stopped: Square,
  }[bot.status];

  return (
    <div
      onClick={onClick}
      className="cursor-pointer rounded-xl border border-white/10 bg-white/5 transition hover:border-cyan-400/40"
    >

      <div className="border-b border-white/10 p-4">

        <div className="flex items-start justify-between">

          <div>

            <div className="flex items-center gap-2">

              <span className="rounded-md bg-cyan-500/10 px-2 py-1 text-xs font-semibold text-cyan-400">
                {bot.strategy}
              </span>

              <span className="text-sm font-medium text-white">
                {bot.asset}
              </span>

            </div>

            <div className="mt-3 flex items-center gap-2">

              <span
                className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs ${statusClass}`}
              >
                <StatusIcon className="h-3 w-3" />
                {bot.status}
              </span>

            </div>

          </div>

          <button className="rounded-lg p-2 text-white/40 transition hover:bg-white/10 hover:text-cyan-400">
            <Settings className="h-4 w-4" />
          </button>

        </div>

      </div>

      <div className="grid grid-cols-2 gap-4 p-4">

        <div>

          <div className="text-xs text-white/40">
            Runtime
          </div>

          <div className="mt-1 text-sm font-medium text-white">
            {bot.runtime}
          </div>

        </div>

        <div>

          <div className="text-xs text-white/40">
            Unrealized PnL
          </div>

          <div className="mt-1 flex items-center gap-1 text-sm font-semibold text-cyan-400">
            <TrendingUp className="h-4 w-4" />
            {bot.pnl}
          </div>

        </div>

      </div>

      <div className="grid grid-cols-3 gap-px border-t border-white/10 bg-white/10">

        <button className="bg-gray-950 py-2 text-xs text-green-400 transition hover:bg-green-500/10">
          Resume
        </button>

        <button className="bg-gray-950 py-2 text-xs text-yellow-400 transition hover:bg-yellow-500/10">
          Pause
        </button>

        <button className="bg-gray-950 py-2 text-xs text-red-400 transition hover:bg-red-500/10">
          Stop
        </button>

      </div>

    </div>
  );
}
