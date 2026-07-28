import BotCard from "./BotCard";

export interface Bot {
  id:string;
  strategy:string;
  asset:string;
  status:"Running"|"Paused"|"Stopped";
  pnl:string;
  runtime:string;
}

const bots: Bot[] = [
  {
    id: "grid-btc",
    strategy: "GRID",
    asset: "BTCUSDT",
    status: "Running",
    pnl: "+245.18",
    runtime: "2d 14h",
  },
  {
    id: "dca-eth",
    strategy: "DCA",
    asset: "ETHUSDT",
    status: "Paused",
    pnl: "+81.44",
    runtime: "18h",
  },
];

interface RunningBotsProps {
  onSelectBot?: (bot: Bot) => void;
}


export default function RunningBots({
  onSelectBot,
}: RunningBotsProps) {
  const running = bots.filter(
    (bot) => bot.status === "Running"
  ).length;

  return (
    <div className="flex h-full flex-col overflow-hidden bg-gray-950">

      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-white">
            Running Bots
          </h2>

          <p className="mt-1 text-xs text-white/50">
            Active strategy instances
          </p>
        </div>

        <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-1 text-xs font-medium text-cyan-400">
          {running} Active
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3">

        {bots.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-white/40">
            No running bots
          </div>
        ) : (
          <div className="space-y-3">
            {bots.map((bot) => (
              <BotCard
                key={bot.id}
                bot={bot}
                onClick={() => onSelectBot?.(bot)}
              />
            ))}
          </div>
        )}

      </div>

    </div>
  );
}
