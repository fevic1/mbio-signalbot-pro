import {
  Bell,
  Wifi,
  Activity,
  Shield,
  Settings,
} from "lucide-react";

export default function TradingHeader() {
  return (
    <header className="h-14 border-b border-white/10 bg-gray-950 px-5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Activity className="h-5 w-5 text-cyan-400" />
        <div>
          <div className="text-white font-semibold">
            Hyperliquid Agent Scout
          </div>
          <div className="text-xs text-white/50">
            Institutional Trading Workspace
          </div>
        </div>
      </div>

      <div className="flex items-center gap-5 text-white/60">
        <div className="flex items-center gap-2">
          <Wifi className="h-4 w-4 text-green-400" />
          <span className="text-xs">CONNECTED</span>
        </div>

        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-cyan-400" />
          <span className="text-xs">AIOS ACTIVE</span>
        </div>

        <button className="hover:text-white transition-colors">
          <Bell className="h-5 w-5" />
        </button>

        <button className="hover:text-white transition-colors">
          <Settings className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
