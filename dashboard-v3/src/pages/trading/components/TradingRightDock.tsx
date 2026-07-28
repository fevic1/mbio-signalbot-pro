import BuilderRouter from "./BuilderRouter";
import RunningBots from "./RunningBots";

export default function TradingRightDock() {
  return (
    <aside className="w-[420px] border-l border-white/10 bg-gray-950 flex flex-col">
      <div className="h-[300px] border-b border-white/10 overflow-y-auto">
        <BuilderRouter />
      </div>

      <div className="flex-1 overflow-y-auto">
        <RunningBots />
      </div>
    </aside>
  );
}
