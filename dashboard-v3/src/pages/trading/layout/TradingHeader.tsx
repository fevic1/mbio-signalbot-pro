import {
  Activity,
  Wifi,
  Bell,
  UserCircle2,
} from "lucide-react";

export default function TradingHeader() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-white/10 bg-gray-950 px-4">

      <div className="flex items-center gap-4">

        <h1 className="text-lg font-semibold tracking-wide text-white">
          MBIO SignalPro
        </h1>

        <span className="rounded-md border border-cyan-500/30 bg-cyan-500/10 px-2 py-1 text-xs font-medium text-cyan-400">
          Trading
        </span>

      </div>

      <div className="flex items-center gap-5">

        <div className="flex items-center gap-2 text-sm text-white/50">
          <Activity className="h-4 w-4 text-green-400" />
          Connected
        </div>

        <div className="flex items-center gap-2 text-sm text-white/50">
          <Wifi className="h-4 w-4 text-cyan-400" />
          Live Feed
        </div>

        <button className="rounded-lg p-2 text-white/50 transition hover:bg-white/10 hover:text-white">
          <Bell className="h-5 w-5" />
        </button>

        <button className="rounded-lg p-2 text-white/50 transition hover:bg-white/10 hover:text-white">
          <UserCircle2 className="h-6 w-6" />
        </button>

      </div>

    </header>
  );
}
