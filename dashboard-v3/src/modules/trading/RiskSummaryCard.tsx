
export function RiskSummaryCard() {

  return (

    <div className="
      rounded-2xl
      border
      border-white/10
      bg-white/5
      p-6
      space-y-6
    ">

      <div className="flex justify-between items-center">

        <h2 className="font-bold text-lg">
          Risk Engine
        </h2>


        <span className="
          rounded-full
          px-3
          py-1
          text-xs
          bg-green-500/10
          text-green-400
        ">
          GREEN
        </span>

      </div>



      <div>

        <div className="
          flex
          justify-between
          text-xs
          text-white/40
          mb-2
        ">

          <span>
            Risk Used
          </span>

          <span>
            18%
          </span>

        </div>


        <div className="
          h-2
          rounded-full
          bg-white/10
          overflow-hidden
        ">

          <div className="
            h-full
            w-[18%]
            bg-green-400
          "/>

        </div>

      </div>



      <div className="
        space-y-4
      ">

        <Metric
          label="Capital Allocation"
          value="2.0%"
        />

        <Metric
          label="Maximum Exposure"
          value="$5,000"
        />

        <Metric
          label="Liquidation Distance"
          value="32%"
        />

      </div>



      <div className="
        rounded-xl
        border
        border-white/10
        p-4
      ">

        <p className="
          text-xs
          uppercase
          text-white/40
          mb-3
        ">
          Risk Controls
        </p>


        <div className="space-y-2 text-sm">

          <Control text="Max Loss Guard" />

          <Control text="Leverage Check" />

          <Control text="Exposure Limit" />

          <Control text="Liquidation Protection" />

        </div>


      </div>


    </div>

  );
}



function Metric({
  label,
  value
}:{
  label:string;
  value:string;
}) {

  return (

    <div className="
      flex
      justify-between
      text-sm
    ">

      <span className="text-white/40">
        {label}
      </span>

      <span className="font-semibold">
        {value}
      </span>

    </div>

  );

}



function Control({
  text
}:{
  text:string;
}) {

  return (

    <div className="
      flex
      items-center
      gap-2
      text-green-400
    ">

      <span>
        ✓
      </span>

      <span>
        {text}
      </span>

    </div>

  );

}
