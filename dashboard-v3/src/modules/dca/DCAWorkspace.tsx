
import { OpenDcaForm } from "./OpenDcaForm";
import { DcaPanel } from "./DcaPanel";


export function DCAWorkspace() {


  const handleClose = (dca: any) => {

    console.log(
      "DCA close requested",
      dca
    );

  };


  const handleResult = (
    msg: string,
    error: boolean
  ) => {

    console.log(
      error ? "ERROR" : "SUCCESS",
      msg
    );

  };


  return (

    <div className="space-y-6">


      <div>

        <h1 className="text-3xl font-bold">
          DCA Engine
        </h1>


        <p className="
          text-sm
          text-white/40
          mt-2
        ">
          Automated accumulation planning and exposure control
        </p>

      </div>




      <div className="
        grid
        grid-cols-4
        gap-4
      ">


        <Metric
          label="Engine"
          value="ACTIVE"
        />


        <Metric
          label="Planning"
          value="AI GENERATED"
        />


        <Metric
          label="Risk"
          value="VALIDATED"
        />


        <Metric
          label="Execution"
          value="READY"
        />


      </div>





      <div className="
        grid
        grid-cols-12
        gap-6
      ">



        <div className="
          col-span-7
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
            DCA Plan Builder
          </h2>


          <OpenDcaForm
            onResult={handleResult}
          />


        </div>





        <div className="
          col-span-5
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
            Active DCA Positions
          </h2>


          <DcaPanel
            onClose={handleClose}
          />


        </div>


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
