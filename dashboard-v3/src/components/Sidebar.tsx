import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, TrendingUp, Brain, Briefcase, 
  Activity, Settings 
} from "lucide-react";

const navItems = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Markets", path: "/markets", icon: TrendingUp },
  { label: "AI Intelligence", path: "/ai", icon: Brain },
  { label: "Trading", path: "/trading", icon: Briefcase },
  { label: "Portfolio", path: "/portfolio", icon: Activity },
  { label: "System", path: "/system", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h1 className="text-lg font-bold text-primary">MBIO SIGNALPRO</h1>
        <p className="text-xs text-muted-foreground">SYSTEM: ONLINE </p>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive 
                  ? "bg-primary/10 text-primary font-medium" 
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
