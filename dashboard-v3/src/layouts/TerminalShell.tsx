import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

import {
  Activity,
  BarChart3,
  Brain,
  Layers,
  Shield,
  Terminal,
  Wallet,
} from "lucide-react";

const NAV = [
  { label: "Trading", path: "trading", icon: Terminal },
  { label: "Execution", path: "execution", icon: Activity },
  { label: "Portfolio", path: "portfolio", icon: Wallet },
  { label: "Markets", path: "markets", icon: BarChart3 },
  { label: "Research", path: "research", icon: Brain },
  { label: "Risk", path: "risk", icon: Shield },
  { label: "System", path: "system", icon: Layers },
  { label: "AIOS", path: "aios", icon: Brain },
];


export default function TerminalShell({
  children,
}: {
  children: React.ReactNode;
}) {

  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {

    const load = async () => {
      try {
        const data = await apiFetch("/overview");
        setOverview(data);
      } catch {
        setOverview(null);
      }
    };

    load();

    const timer = setInterval(load, 10000);

    return () => clearInterval(timer);

  }, []);

  return (
    <div className="min-h-screen bg-black text-white flex">

      <aside className="w-72 border-r border-white/10 bg-black/60 backdrop-blur-xl p-6 relative">

        <div className="mb-10">
          <h1 className="text-xl font-bold">
            MBIO
          </h1>

          <p className="text-xs text-white/40 mt-1">
            SIGNALPRO TERMINAL
          </p>
        </div>


        <nav className="space-y-2">

          {NAV.map(({ label, path, icon: Icon }) => (

            <a
              key={path}
              target={path === "aios" ? "_blank" : undefined}
              rel={path === "aios" ? "noopener noreferrer" : undefined}
              href={path === "aios" ? "http://172.238.11.219:8001/aios/" : `/pages/${path}/`}
              className="
                w-full
                flex
                items-center
                gap-3
                rounded-xl
                px-4
                py-3
                text-sm
                text-white/60
                hover:text-white
                hover:bg-white/10
                transition
              "
            >

              <Icon size={18}/>

              {label}

            </a>

          ))}

        </nav>


        <div className="absolute bottom-6 left-6 right-6 rounded-xl border border-green-500/20 bg-green-500/5 p-4">

          <div className="flex items-center gap-2 text-green-400 text-sm">

            <span className="h-2 w-2 rounded-full bg-green-400"/>

            SYSTEM ONLINE

          </div>


          <p className="text-xs text-white/40 mt-2">
            Execution Gateway Connected
          </p>

        </div>

      </aside>


      <main className="flex-1 p-8 overflow-auto">


        <div className="grid grid-cols-4 gap-4 mb-8">

          <Metric
            title="Capital"
            value={
              overview
                ? `$${Number(overview.total_balance).toFixed(2)}`
                : "—"
            }
          />

          <Metric
            title="Risk Used"
            value={
              overview
                ? `${Number(overview.deployed_pct).toFixed(1)}%`
                : "—"
            }
          />

          <Metric
            title="Positions"
            value={
              overview
                ? String(overview.open_positions)
                : "—"
            }
          />

          <Metric
            title="Execution"
            value="ONLINE"
          />

        </div>


        {children}


      </main>


    </div>
  );
}


function Metric({
  title,
  value,
}: {
  title:string;
  value:string;
}) {

  return (

    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">

      <p className="text-xs text-white/40 uppercase">
        {title}
      </p>

      <p className="mt-3 text-2xl font-semibold">
        {value}
      </p>

    </div>

  );
}
