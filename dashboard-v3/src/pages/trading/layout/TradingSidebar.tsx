import {
  LayoutDashboard,
  CandlestickChart,
  Wallet,
  BarChart3,
  Search,
  Cpu,
  Settings,
} from "lucide-react";

const items = [
  { icon: LayoutDashboard, label: "Dashboard" },
  { icon: CandlestickChart, label: "Trading", active: true },
  { icon: Wallet, label: "Portfolio" },
  { icon: BarChart3, label: "Markets" },
  { icon: Search, label: "Research" },
  { icon: Cpu, label: "Execution" },
  { icon: Settings, label: "System" },
];

export default function TradingSidebar() {
  return (
    <aside className="flex w-16 shrink-0 flex-col border-r border-white/10 bg-gray-950">

      <div className="flex flex-1 flex-col items-center gap-2 py-3">

        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              title={item.label}
              className={[
                "flex h-11 w-11 items-center justify-center rounded-xl transition-all",
                item.active
                  ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/30"
                  : "text-white/40 hover:bg-white/5 hover:text-white",
              ].join(" ")}
            >
              <Icon className="h-5 w-5" />
            </button>
          );
        })}

      </div>

      <div className="border-t border-white/10 p-2">

        <button
          title="Settings"
          className="flex h-11 w-11 items-center justify-center rounded-xl text-white/40 transition hover:bg-white/5 hover:text-white"
        >
          <Settings className="h-5 w-5" />
        </button>

      </div>

    </aside>
  );
}
