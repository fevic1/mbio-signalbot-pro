
import { OrdersPanel } from "./OrdersPanel";
import { ActivityPanel } from "./ActivityPanel";
import { ExecutionTelemetryPanel } from "./ExecutionTelemetryPanel";


export function ExecutionWorkspace() {

  return (

    <div className="space-y-6">


      <div>

        <h1 className="text-3xl font-bold">
          Execution Control Center
        </h1>

        <p className="
          text-sm
          text-white/40
          mt-2
        ">
          Live order lifecycle monitoring
        </p>

      </div>



      <div className="
        grid
        grid-cols-4
        gap-4
      ">

        <Metric
          label="Execution Status"
          value="ONLINE"
        />

        <Metric
          label="Active Orders"
          value="LIVE"
        />

        <Metric
          label="Routing"
          value="CONNECTED"
        />

        <Metric
          label="Latency"
          value="83ms"
        />

      </div>



      <div className="
        rounded-2xl
        border
        border-white/10
        bg-white/5
        p-6
      ">

        <h2 className="font-bold mb-5">
          Active Execution
        </h2>

        <OrdersPanel />

      </div>



      <div className="
        rounded-2xl
        border
        border-white/10
        bg-white/5
        p-6
      ">

        <h2 className="font-bold mb-5">
          Execution Activity
        </h2>

        <ActivityPanel />

      </div>


      <ExecutionTelemetryPanel />


    </div>

  );
}



function Metric({
  label,
  value,
}:{
  label:string;
  value:string;
}) {

  return (

    <div className="
      rounded-xl
      border
      border-white/10
      bg-white/5
      p-4
    ">

      <p className="
        text-xs
        uppercase
        text-white/40
      ">
        {label}
      </p>


      <p className="
        mt-2
        font-bold
      ">
        {value}
      </p>


    </div>

  );

}
