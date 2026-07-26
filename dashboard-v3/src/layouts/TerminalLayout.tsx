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
  ["Trading", Terminal],
  ["Execution", Activity],
  ["Portfolio", Wallet],
  ["Markets", BarChart3],
  ["Research", Brain],
  ["Risk", Shield],
  ["System", Layers],
];


export default function TerminalLayout({
  children,
  active,
  onNavigate,
}: {
  children: React.ReactNode;
  active: string;
  onNavigate: (page: string) => void;
}) {

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

          {NAV.map(([label, Icon]) => (

            <button
              key={label as string}
              onClick={() => onNavigate((label as string).toLowerCase())}
              className={`
                w-full
                flex
                items-center
                gap-3
                rounded-xl
                px-4
                py-3
                text-sm
                transition
                ${
                  active === (label as string).toLowerCase()
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:text-white hover:bg-white/10"
                }
              `}
            >

              <Icon size={18}/>

              {label as string}

            </button>

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

          <Metric title="Capital" value="$25,430"/>

          <Metric title="Risk Used" value="18%"/>

          <Metric title="Market Regime" value="SIDEWAYS"/>

          <Metric title="Execution" value="ONLINE"/>

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
