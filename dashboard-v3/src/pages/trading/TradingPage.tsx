import { useState } from "react";
import { WatchlistPanel } from "@/components/WatchlistPanel";
import { CandleChart } from "@/modules/markets/CandleChart";
import { PositionsPanel } from "@/modules/portfolio/PositionsPanel";
import { TradingTerminal } from "./layout/TradingTerminal";
import { QTParametersPanel } from "./layout/QTParametersPanel";

type Props = {
  setTicketCtx: (ctx: any) => void;
  positionRefreshKey: number;
  triggerPositionRefresh: () => void;
};

const TABS = [
  "Positions",
  "Orders",
  "Signals",
  "History",
  "AI",
  "Logs",
  "Alerts",
] as const;

export default function TradingPage({
  setTicketCtx,
  positionRefreshKey,
}: Props) {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>("Positions");

  // Left Panel: Watchlist (dynamic height)
  const leftPanel = (
    <div className="h-full lg:block hidden">
      <WatchlistPanel />
    </div>
  );

  // Center Panel: Chart + Bottom Workspace (dynamic heights, no scrolling)
  const centerPanel = (
    <div className="flex h-full flex-col bg-background">
      {/* Chart Section: Takes 60% of available height dynamically */}
      <div className="flex-[3] min-h-0 border-b border-border">
        <CandleChart />
      </div>
      
      {/* Bottom Workspace: Takes 40% of available height, internal scroll only */}
      <div className="flex-[2] min-h-0 flex-col bg-card overflow-hidden flex">
        <div className="flex border-b border-border overflow-x-auto flex-shrink-0">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-xs font-medium whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto p-3">
          {activeTab === "Positions" ? (
            <PositionsPanel
              refreshKey={positionRefreshKey}
              onClose={(pos) =>
                setTicketCtx({
                  type: "close_position",
                  asset: pos.asset,
                  side: pos.side,
                  size: pos.size,
                })
              }
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              {activeTab} coming soon
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Right Panel: QT Parameters (dynamic height)
  const rightPanel = (
    <QTParametersPanel 
      onDeploy={() => setTicketCtx({ type: "create_bot_choice" })} 
    />
  );

  return (
    <TradingTerminal
      leftPanel={leftPanel}
      centerPanel={centerPanel}
      rightPanel={rightPanel}
    />
  );
}
