
type Props = {
  asset?: string;
  label?: string;
  strategy?: string;
  regime?: string;
  confidence?: number;
  executionType?: string;
};


export function ExecutionIntentCard({
  asset = "ETH-PERP",
  label = "QT_ENTRY",
  strategy = "HUNTER_FILL",
  regime = "SIDEWAYS",
  confidence = 87,
  executionType = "MARKET",
}: Props) {

  return (
    <div className="
      rounded-2xl
      border
      border-white/10
      bg-white/5
      p-6
      space-y-6
    ">

      <div className="flex justify-between items-start">

        <div>
          <p className="text-xs uppercase text-white/40">
            Execution Intent
          </p>

          <h2 className="text-2xl font-bold mt-2">
            {asset}
          </h2>
        </div>


        <div className="
          rounded-full
          px-3
          py-1
          text-xs
          bg-green-500/10
          text-green-400
        ">
          READY ✓
        </div>

      </div>



      <div className="
        grid
        grid-cols-3
        gap-4
      ">

        <Metric
          title="Label"
          value={label}
        />

        <Metric
          title="Strategy"
          value={strategy}
        />

        <Metric
          title="Execution"
          value={executionType}
        />

        <Metric
          title="Market Regime"
          value={regime}
        />

        <Metric
          title="Signal Confidence"
          value={`${confidence}%`}
        />

        <Metric
          title="Risk Check"
          value="PASSED ✓"
        />

      </div>



      <div className="
        border
        border-white/10
        rounded-xl
        p-4
      ">

        <p className="text-xs uppercase text-white/40 mb-3">
          Execution Pipeline
        </p>


        <div className="
          grid
          grid-cols-4
          gap-3
          text-xs
        ">

          <Stage text="Intent Created" />
          <Stage text="Validated" />
          <Stage text="Submitted" />
          <Stage text="Filled" />

        </div>

      </div>


    </div>
  );
}



function Stage({
  text
}:{
  text:string;
}) {

  return (

    <div className="
      rounded-lg
      border
      border-green-500/20
      bg-green-500/10
      p-3
      text-green-400
      text-center
    ">

      ✓ {text}

    </div>

  );

}



function Metric({
  title,
  value,
}: {
  title:string;
  value:string;
}) {

  return (

    <div>

      <p className="
        text-xs
        uppercase
        text-white/40
      ">
        {title}
      </p>


      <p className="
        mt-1
        font-semibold
      ">
        {value}
      </p>

    </div>

  );

}
