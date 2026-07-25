import AppShell from "./AppShell";

import { QuickTicket } from "@/modules/trading/QuickTicket";
import { OrdersPanel } from "@/modules/execution/OrdersPanel";
import { PositionsPanel } from "@/modules/portfolio/PositionsPanel";
import { OpenDcaForm } from "@/modules/dca/OpenDcaForm";

export default function Router() {

  const handleResult = (
    msg: string,
    isError: boolean
  ) => {
    console.log(
      isError ? "ERROR:" : "SUCCESS:",
      msg
    );
  };


  const handleClose = (position: any) => {
    console.log(
      "close position requested",
      position
    );
  };


  return (
    <AppShell>

      <div className="space-y-8">

        <section>
          <h2 className="text-xl font-bold">
            Execution Terminal
          </h2>

          <QuickTicket />
        </section>


        <section>
          <h2 className="text-xl font-bold">
            Execution Monitor
          </h2>

          <OrdersPanel />
        </section>


        <section>
          <h2 className="text-xl font-bold">
            Portfolio Command Center
          </h2>

          <PositionsPanel
            onClose={handleClose}
          />
        </section>


        <section>
          <h2 className="text-xl font-bold">
            DCA Engine
          </h2>

          <OpenDcaForm
            onResult={handleResult}
          />
        </section>

      </div>

    </AppShell>
  );
}
