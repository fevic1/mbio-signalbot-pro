import CreateBotButton from "./CreateBotButton";
import BotCard from "./BotCard";

const bots = [
  {
    id: "GRID-BTC-001",
    strategy: "GRID",
    symbol: "BTCUSDT",
    status: "RUNNING",
    pnl: "+124.82",
  },
  {
    id: "DCA-ETH-002",
    strategy: "DCA",
    symbol: "ETHUSDT",
    status: "PAUSED",
    pnl: "-18.45",
  },
];

export default function RunningBots() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <div>
          <h2 className="text-white font-semibold">
            Strategy Bots
          </h2>

          <p className="text-xs text-white/50">
            Active and saved strategies
          </p>
        </div>

        <CreateBotButton />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {bots.map((bot) => (
          <BotCard
            key={bot.id}
            {...bot}
          />
        ))}
      </div>
    </div>
  );
}
