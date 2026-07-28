import {
  LayoutDashboard,
  CandlestickChart,
  Bot,
  Activity,
  Wallet,
  Settings,
  BarChart3,
  Shield,
} from "lucide-react";

const items = [
  LayoutDashboard,
  CandlestickChart,
  Bot,
  Activity,
  Wallet,
  BarChart3,
  Shield,
  Settings,
];

export default function TradingSidebar() {
  return (
    <aside className="w-16 border-r border-white/10 bg-gray-950 flex flex-col items-center py-4 gap-3">
      {items.map((Icon, index) => (
        <button
          key={index}
          className="w-10 h-10 rounded-lg flex items-center justify-center text-white/60 hover:text-cyan-400 hover:bg-white/5 transition-all"
        >
          <Icon className="h-5 w-5" />
        </button>
      ))}
    </aside>
  );
}
