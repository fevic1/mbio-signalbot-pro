import AppShell from "./AppShell";

import { TradingWorkspace } from "@/modules/trading/TradingWorkspace";
import { ExecutionWorkspace } from "@/modules/execution/ExecutionWorkspace";
import { PortfolioWorkspace } from "@/modules/portfolio/PortfolioWorkspace";
import { DCAWorkspace } from "@/modules/dca/DCAWorkspace";
import { MarketsWorkspace } from "@/modules/markets/MarketsWorkspace";
import { ResearchWorkspace } from "@/modules/research/ResearchWorkspace";
import { SystemWorkspace } from "@/modules/system/SystemWorkspace";


export default function Router() {

  return (
    <AppShell>

      <div className="space-y-8">

        <TradingWorkspace />

        <ExecutionWorkspace />

        <PortfolioWorkspace />

        <DCAWorkspace />

        <MarketsWorkspace />

        <ResearchWorkspace />

        <SystemWorkspace />

      </div>

    </AppShell>
  );
}
