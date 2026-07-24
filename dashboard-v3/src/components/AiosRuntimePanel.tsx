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
    <Card>
      <CardHeader>
        AIOS Runtime
      </CardHeader>

      <CardContent>
        {data ? (
          <div className="space-y-2">
            <div>Status: {data.runtime}</div>
            <div>Capabilities: {data.capabilities}</div>
            <div>
              Workflow Engine: {data.workflows ? "ACTIVE" : "OFF"}
            </div>
            <div>
              Decision Engine: {data.decision_engine ? "ACTIVE" : "OFF"}
            </div>
            <div>
              Execution Planner: {data.execution_planner ? "ACTIVE" : "OFF"}
            </div>
          </div>
        ) : (
          <div>AIOS unavailable</div>
        )}
      </CardContent>
    </Card>
  )
}
