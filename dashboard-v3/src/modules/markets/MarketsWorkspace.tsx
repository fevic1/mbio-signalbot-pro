
import AssetsTable from "./AssetsTable";
import { CandleChart } from "./CandleChart";
import { RegimePanel } from "./RegimePanel";


export function MarketsWorkspace() {

  return (

    <div className="space-y-6">


      <div>

        <h1 className="
          text-3xl
          font-bold
        ">
          Markets Intelligence
        </h1>


        <p className="
          mt-2
          text-sm
          text-white/40
        ">
          Institutional market analysis and asset discovery terminal
        </p>

      </div>




      <RegimePanel />





      <div className="
        grid
        grid-cols-12
        gap-6
      ">


        <div className="
          col-span-5
          rounded-2xl
          border
          border-white/10
          bg-white/5
          p-6
        ">


          <h2 className="
            mb-4
            font-bold
          ">
            Asset Universe
          </h2>


          <AssetsTable />


        </div>





        <div className="
          col-span-7
          rounded-2xl
          border
          border-white/10
          bg-white/5
          p-6
        ">


          <h2 className="
            mb-4
            font-bold
          ">
            Price Action
          </h2>


          <CandleChart />


        </div>


      </div>


    </div>

  );

}
