import { QuickTicket } from "./QuickTicket";
import { ExecutionIntentCard } from "./ExecutionIntentCard";
import { RiskSummaryCard } from "./RiskSummaryCard";

import { CandleChart } from "@/modules/markets/CandleChart";
import { RegimePanel } from "@/modules/markets/RegimePanel";


export function TradingWorkspace() {

  return (

    <div className="space-y-6">


      <div>

        <h1 className="text-3xl font-bold">
          Execution Terminal
        </h1>

        <p className="text-sm text-white/40 mt-2">
          Institutional order execution workspace
        </p>

      </div>



      <ExecutionIntentCard />



      <div className="
        grid
        grid-cols-12
        gap-6
      ">


        <div className="
          col-span-8
          rounded-2xl
          border
          border-white/10
          bg-white/5
          p-6
        ">

          <RegimePanel />

          <div className="mt-6">

            <CandleChart />

          </div>

        </div>



        <div className="
          col-span-4
          space-y-6
        ">


          <RiskSummaryCard />


          <div className="
            rounded-2xl
            border
            border-white/10
            bg-white/5
            p-6
          ">

            <QuickTicket />

          </div>


        </div>


      </div>


    </div>

  );
}
