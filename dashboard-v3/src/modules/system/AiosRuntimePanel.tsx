import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { aiosTelemetry } from "@/lib/api"

type AiosTelemetry = {
  runtime: string
  capabilities: number
  workflows: boolean
  decision_engine: boolean
  execution_planner: boolean
}

export function AiosRuntimePanel() {
  const [data, setData] = useState<AiosTelemetry | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const result = await aiosTelemetry<AiosTelemetry>()
        setData(result)
      } catch {
        setData(null)
      }
    }

    load()

    const timer = setInterval(load, 10000)

    return () => clearInterval(timer)
  }, [])

  return (
    <Card className="
  rounded-2xl
  border-white/10
  bg-white/5
">
      <CardHeader>
        ⚡ AIOS Runtime Core
      </CardHeader>

      <CardContent>
        {data ? (
          <div className="
  grid
  grid-cols-2
  gap-4
">
            <Metric
 label="Runtime"
 value={data.runtime}
/>
            <Metric
 label="Capabilities"
 value={String(data.capabilities)}
/>
            <Metric
 label="Workflow Engine"
 value={data.workflows ? "ACTIVE" : "OFF"}
/>
            <Metric
 label="Decision Engine"
 value={data.decision_engine ? "ACTIVE" : "OFF"}
/>
            <Metric
 label="Execution Planner"
 value={data.execution_planner ? "ACTIVE" : "OFF"}
/>
          </div>
        ) : (
          <div>AIOS unavailable</div>
        )}
      </CardContent>
    </Card>
  )
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
    rounded-xl
    border
    border-white/10
    bg-black/20
    p-4
  ">
    <div className="text-xs text-white/40">
      {label}
    </div>

    <div className="mt-2 font-bold">
      {value}
    </div>
  </div>
 )
}
