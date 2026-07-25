import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ActivityEvent {
  timestamp: string
  event_type: string
  asset: string
  strategy: string
  side: string
  size: number
  price: number
  pnl: number
  order_id: string | null
}

const POLL_INTERVAL_MS = 15_000

const EVENT_LABEL: Record<string, string> = {
  open: "Open",
  close: "Close",
  partial_close: "Partial Close",
  grid_fill: "Grid Fill",
  grid_tp: "Grid TP",
}

export function ActivityPanel() {
  const [events, setEvents] = useState<ActivityEvent[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchActivity = useCallback(async () => {
    try {
      const res = await apiFetch<{ activity: ActivityEvent[]; count: number }>("/activity")
      setEvents(res.activity)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load activity")
    }
  }, [])

  useEffect(() => {
    fetchActivity()
    const id = setInterval(fetchActivity, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchActivity])

  if (error && !events) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
  }
  if (!events) {
    return <p className="text-sm text-muted-foreground">Loading activity…</p>
  }
  if (events.length === 0) {
    return <p className="text-sm text-muted-foreground">No trade activity recorded yet.</p>
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-xs text-warn">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      <div className="
        rounded-xl
        border
        border-white/10
        overflow-hidden
      ">

      <table className="w-full text-sm">
        <thead className="bg-white/5">
          <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground">

            <th className="p-3 font-normal">Time</th>
            <th className="p-3 font-normal">Asset</th>
            <th className="p-3 font-normal">Lifecycle</th>
            <th className="p-3 font-normal">Strategy</th>
            <th className="p-3 font-normal">Execution</th>
            <th className="p-3 font-normal">PnL</th>

          </tr>
        </thead>
        <tbody className="font-mono">
          {events.map((e, i) => (
            <tr key={`${e.order_id ?? i}-${e.timestamp}`} className="border-t border-border">
              <td className="p-3 text-muted-foreground">
                {new Date(e.timestamp).toLocaleString()}
              </td>

              <td className="p-3 font-sans font-semibold">
                {e.asset}
              </td>

              <td className="p-3">
                <span className="
                  rounded-full
                  px-2
                  py-1
                  text-xs
                  bg-blue-500/10
                  text-blue-400
                ">
                  {EVENT_LABEL[e.event_type] ?? e.event_type}
                </span>
              </td>

              <td className="p-3 text-muted-foreground">
                {e.strategy}
              </td>

              <td className="p-3">
                <Badge variant={e.side === "BUY" ? "long" : "short"}>
                  {e.side}
                </Badge>
              </td>

              <td className={cn(
                "p-3",
                e.pnl > 0
                  ? "text-long"
                  : e.pnl < 0
                    ? "text-short"
                    : "text-muted-foreground"
              )}>
                {e.pnl !== 0
                  ? `${e.pnl >= 0 ? "+" : ""}$${e.pnl.toFixed(4)}`
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      </div>
    </div>
  )
}
