import { useState, useCallback } from "react";
import TradingPage from "@/pages/trading/TradingPage";

export function TradingWorkspace() {
  const [, setTicketCtx] = useState<any>(null);
  const [positionRefreshKey, setPositionRefreshKey] = useState(0);

  const triggerPositionRefresh = useCallback(() => {
    setPositionRefreshKey((k) => k + 1);
  }, []);

  return (
    <div className="h-full w-full p-4 overflow-hidden">
      <div className="flex flex-col h-full gap-4">
        <div className="flex-1 min-h-0">
          <TradingPage
            setTicketCtx={setTicketCtx}
            positionRefreshKey={positionRefreshKey}
            triggerPositionRefresh={triggerPositionRefresh}
          />
        </div>
      </div>
    </div>
  );
}
