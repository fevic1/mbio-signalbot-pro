import { useEffect, useState } from "react"
import { apiFetch } from "@/lib/api"

interface RiskStatus {
  status: string
  risk_used_pct: number
  capital_allocation_pct: number
  total_exposure: number
  max_exposure: number
  active_positions: number
  max_positions: number
  controls: {
    max_loss_guard: boolean
    leverage_check: boolean
    exposure_limit: boolean
    liquidation_protection: boolean
  }
}

export function RiskSummaryCard() {

  const [risk, setRisk] = useState<RiskStatus | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch<RiskStatus>("/risk/status")
        setRisk(data)
      } catch {
        setRisk(null)
      }
    }

    load()

    const timer = setInterval(load, 10000)

    return () => clearInterval(timer)
  }, [])

  const status = risk?.status ?? "UNKNOWN"

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
          {status}
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
            {risk ? `${risk.risk_used_pct}%` : "—"}
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
            w-[0%]
            bg-green-400
          "/>

        </div>

      </div>



      <div className="
        space-y-4
      ">

        <Metric
          label="Capital Allocation"
          value={risk ? `${risk.capital_allocation_pct}%` : "—"}
        />

        <Metric
          label="Maximum Exposure"
          value={risk ? `$${risk.max_exposure.toLocaleString()}` : "—"}
        />

        <Metric
          label="Liquidation Distance"
          value={risk ? `${risk.active_positions}/${risk.max_positions}` : "—"}
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

          <Control text="Max Loss Guard" enabled={risk?.controls.max_loss_guard} />

          <Control text="Leverage Check" enabled={risk?.controls.leverage_check} />

          <Control text="Exposure Limit" enabled={risk?.controls.exposure_limit} />

          <Control text="Liquidation Protection" enabled={risk?.controls.liquidation_protection} />

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
  text,
  enabled = false
}:{
  text:string;
  enabled?: boolean;
}) {

  void enabled;

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
