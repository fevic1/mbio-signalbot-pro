import { useState } from "react";
import { CandleChart } from "@/modules/markets/CandleChart";
import { PositionsPanel } from "@/modules/portfolio/PositionsPanel";
import { TicketContext } from "@/components/Ticket";

const TABS = [
  "Positions",
  "Orders",
  "Signals",
  "History",
  "AI",
  "Logs",
  "Alerts",
] as const;

interface TradingCenterProps {
  positionRefreshKey: number;
  gridRefreshKey: number;
  triggerGridRefresh: () => void;
  notify: (msg: string, isError?: boolean) => void;
  setTicketCtx: (ctx: TicketContext) => void;
}

export default function TradingCenter({
  positionRefreshKey,
  setTicketCtx,
}: TradingCenterProps) {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>("Positions");

  return (
    <div className="flex flex-1 min-h-0 flex-col gap-3">
      {/* Chart Section - Fixed height, auto-adjusts */}
      <div className="h-[420px] rounded-md border border-border bg-card p-3 flex-shrink-0">
        <CandleChart />
      </div>

      {/* Bottom Tabs Section - Flexible height, independent scroll */}
      <div className="flex min-h-0 flex-1 flex-col rounded-md border border-border bg-card">
        <div className="flex border-b border-border overflow-x-auto flex-shrink-0">
          {TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-sm whitespace-nowrap ${
                activeTab === tab
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-3">
          {activeTab === "Positions" && (
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
          )}

          {activeTab !== "Positions" && (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              {activeTab} coming soon
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
