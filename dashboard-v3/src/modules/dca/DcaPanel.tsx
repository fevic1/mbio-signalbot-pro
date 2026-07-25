import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Square } from "lucide-react"

interface DcaPosition {
  asset: string
  direction: string
  levels: number
  filled_levels: number
  active_orders: number
  base_size: number
  total_invested: number
  avg_entry: number
  entry: number
  enabled: boolean
  sl?: number
  tp1?: number
  tp2?: number
  tp3?: number
}

const POLL_INTERVAL_MS = 10_000

export function DcaPanel({ onClose }: { onClose: (dca: DcaPosition) => void }) {
  const [positions, setPositions] = useState<DcaPosition[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchDca = useCallback(async () => {
    try {
      const res = await apiFetch<{ positions: DcaPosition[]; count: number }>("/dca_status")
      setPositions(res.positions)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load DCA positions")
    }
  }, [])

  useEffect(() => {
    fetchDca()
    const id = setInterval(fetchDca, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchDca])

  if (error && !positions) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
  }
  if (!positions) {
    return <p className="text-sm text-muted-foreground">Loading DCA positions…</p>
  }
  if (positions.length === 0) {
    return <p className="text-sm text-muted-foreground">No active DCA positions.</p>
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-xs text-warn">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      {positions.map((d) => (
        <Card key={d.asset}>
          <CardHeader>
            <div className="flex items-center gap-3">
              <span className="font-semibold">{d.asset}</span>
              <Badge variant={d.direction === "LONG" ? "long" : "short"}>{d.direction}</Badge>
              <span className="font-mono text-xs text-muted-foreground">
                {d.filled_levels}/{d.levels} levels · {d.active_orders} active
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Button size="icon" variant="ghost" onClick={() => onClose(d)} title="Close DCA position">
                <Square className="h-3.5 w-3.5 text-short" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4 text-xs font-mono">
              <div>
                <div className="text-muted-foreground">Entry</div>
                <div>${d.entry.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Avg Entry</div>
                <div>${d.avg_entry.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Base Size</div>
                <div>{d.base_size}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Invested</div>
                <div>${d.total_invested.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Stop Loss</div>
                <div className="text-red-400">${d.sl ? d.sl.toLocaleString() : "—"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Take Profit 1</div>
                <div className="text-green-400">${d.tp1 ? d.tp1.toLocaleString() : "—"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Take Profit 2</div>
                <div className="text-green-400">${d.tp2 ? d.tp2.toLocaleString() : "—"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Take Profit 3</div>
                <div className="text-green-400">${d.tp3 ? d.tp3.toLocaleString() : "—"}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
