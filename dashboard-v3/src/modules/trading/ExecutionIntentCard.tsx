type Props = {
  asset?: string;
  label?: string;
  strategy?: string;
  regime?: string;
  confidence?: number;
};


export function ExecutionIntentCard({
  asset = "ETH-PERP",
  label = "QT_ENTRY",
  strategy = "HUNTER_FILL",
  regime = "SIDEWAYS",
  confidence = 87,
}: Props) {

  return (
    <div className="
      rounded-2xl
      border
      border-white/10
      bg-white/5
      p-6
    ">

      <div className="flex justify-between">

        <div>
          <p className="text-xs text-white/40 uppercase">
            Order Intent
          </p>

          <h2 className="text-xl font-bold mt-2">
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
          VALIDATED ✓
        </div>

      </div>


      <div className="grid grid-cols-2 gap-4 mt-6">


        <Metric
          title="Execution Label"
          value={label}
        />

        <Metric
          title="Strategy"
          value={strategy}
        />

        <Metric
          title="Regime"
          value={regime}
        />

        <Metric
          title="Signal Confidence"
          value={`${confidence}%`}
        />


      </div>


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

      <p className="text-xs text-white/40">
        {title}
      </p>

      <p className="font-semibold mt-1">
        {value}
      </p>

    </div>
  );
}
