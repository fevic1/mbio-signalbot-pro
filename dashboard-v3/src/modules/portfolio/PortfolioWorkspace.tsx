
import { OverviewPanel } from "./OverviewPanel";
import { PositionsPanel } from "./PositionsPanel";


export function PortfolioWorkspace() {

  const handleClose = (position: any) => {
    console.log(
      "close requested",
      position
    );
  };


  return (

    <div className="space-y-6">


      <div>

        <h1 className="text-3xl font-bold">
          Portfolio Command Center
        </h1>

        <p className="
          text-sm
          text-white/40
          mt-2
        ">
          Capital allocation, exposure and position control
        </p>

      </div>



      <div className="
        grid
        grid-cols-4
        gap-4
      ">


        <Metric
          label="Portfolio State"
          value="ACTIVE"
        />


        <Metric
          label="Capital"
          value="CONNECTED"
        />


        <Metric
          label="Risk State"
          value="GREEN"
        />


        <Metric
          label="Execution"
          value="ONLINE"
        />


      </div>



      <div className="
        rounded-2xl
        border
        border-white/10
        bg-white/5
        p-6
      ">

        <OverviewPanel />

      </div>




      <div className="
        rounded-2xl
        border
        border-white/10
        bg-white/5
        p-6
      ">

        <h2 className="
          font-bold
          mb-5
        ">
          Active Positions
        </h2>


        <PositionsPanel
          onClose={handleClose}
        />


      </div>


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
