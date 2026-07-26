import { useState } from "react";

import AppShell from "./AppShell";
import { type Workspace } from "./workspaces";

import { TradingWorkspace } from "@/modules/trading/TradingWorkspace";
import { ExecutionWorkspace } from "@/modules/execution/ExecutionWorkspace";
import { PortfolioWorkspace } from "@/modules/portfolio/PortfolioWorkspace";
import { DCAWorkspace } from "@/modules/dca/DCAWorkspace";
import { MarketsWorkspace } from "@/modules/markets/MarketsWorkspace";
import { ResearchWorkspace } from "@/modules/research/ResearchWorkspace";
import { SystemWorkspace } from "@/modules/system/SystemWorkspace";


const workspaceMap = {
  trading: TradingWorkspace,
  execution: ExecutionWorkspace,
  portfolio: PortfolioWorkspace,
  dca: DCAWorkspace,
  markets: MarketsWorkspace,
  research: ResearchWorkspace,
  system: SystemWorkspace,
};


export default function Router() {

  const [active] = useState<Workspace>("trading");


  const WorkspaceComponent =
    workspaceMap[active];


  return (
    <AppShell>

      <WorkspaceComponent />

    </AppShell>
  );
}
