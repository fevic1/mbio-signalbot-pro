import { useEffect, useState } from "react"
import { apiFetch } from "@/lib/api"

interface ExecutionEvent {
  type: string
  timestamp: string
  payload: Record<string, unknown>
}

export function ExecutionTelemetryPanel() {

  const [events, setEvents] = useState<ExecutionEvent[]>([])

  useEffect(() => {

    const load = async () => {
      try {
        const data = await apiFetch<{
          events: ExecutionEvent[]
        }>("/execution/events")

        setEvents(data.events || [])

      } catch {
        setEvents([])
      }
    }

    load()

    const timer = setInterval(load, 5000)

    return () => clearInterval(timer)

  }, [])


  return (
    <div className="
      rounded-2xl
      border
      border-white/10
      bg-white/5
      p-6
    ">

      <h2 className="font-bold mb-5">
        AIOS Execution Telemetry
      </h2>


      {events.length === 0 ? (

        <p className="text-sm text-white/40">
          No execution events
        </p>

      ) : (

        <div className="space-y-3">

          {events.slice().reverse().map((event, index) => (

            <div
              key={`${event.timestamp}-${index}`}
              className="
                rounded-lg
                border
                border-white/10
                p-3
              "
            >

              <div className="flex justify-between">

                <span className="font-semibold">
                  {event.type}
                </span>

                <span className="text-xs text-white/40">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>

              </div>


              <pre className="
                mt-2
                text-xs
                text-white/50
                overflow-auto
              ">
                {JSON.stringify(event.payload, null, 2)}
              </pre>

            </div>

          ))}

        </div>

      )}

    </div>
  )
}
