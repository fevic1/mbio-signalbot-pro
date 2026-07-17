import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Square, Pause, Pencil } from "lucide-react"

interface Grid {
  key: string
  asset: string
  enabled: boolean
  mode: string
  lower_price: number
  upper_price: number
  step_size: number
  grid_quantity: number
  nodes_active: number
  nodes_total: number
  cycles: number
  realized_pnl: number
  investment: number
}

const POLL_INTERVAL_MS = 10_000

export function GridBotsPanel({ onClose }: { onClose: (grid: Grid) => void }) {
  const [grids, setGrids] = useState<Grid[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchGrids = useCallback(async () => {
    try {
      const res = await apiFetch<{ grids: Grid[]; count: number }>("/grids")
      setGrids(res.grids)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load grids")
    }
  }, [])

  useEffect(() => {
    fetchGrids()
    const id = setInterval(fetchGrids, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchGrids])

  if (error && !grids) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
  }

  if (!grids) {
    return <p className="text-sm text-muted-foreground">Loading grid bots…</p>
  }

  return (
    <div className="space-y-3">
      {grids.length === 0 ? (
        <div className="rounded-md border border-dashed border-muted-foreground/30 p-8 text-center">
          <p className="text-sm text-muted-foreground">No active grid bots.</p>
          <p className="text-xs text-muted-foreground/60 mt-1">Click "+ Open New Grid Bot" above to start.</p>
        </div>
      ) : (
        <>
      {error && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-xs text-warn">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      {grids.map((g) => (
        <Card key={g.key}>
          <CardHeader>
            <div className="flex items-center gap-3">
              <span className="font-semibold">{g.asset}</span>
              <Badge variant={g.enabled ? "long" : "default"}>{g.enabled ? "Active" : "Inactive"}</Badge>
              <span className="font-mono text-xs text-muted-foreground">{g.nodes_active}/{g.nodes_total} nodes</span>
            </div>
            <div className="flex items-center gap-1">
              <Button size="icon" variant="ghost" disabled title="No pause/resume endpoint exists yet on the backend">
                <Pause className="h-3.5 w-3.5 text-muted-foreground/40" />
              </Button>
              <Button size="icon" variant="ghost" disabled title="No edit-range endpoint exists yet — see Ticket for details">
                <Pencil className="h-3.5 w-3.5 text-muted-foreground/40" />
              </Button>
              <Button size="icon" variant="ghost" onClick={() => onClose(g)} title="Close grid">
                <Square className="h-3.5 w-3.5 text-short" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4 text-xs font-mono">
              <div>
                <div className="text-muted-foreground">Range</div>
                <div>${g.lower_price.toLocaleString()} – ${g.upper_price.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Cycles</div>
                <div>{g.cycles}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Realized PnL</div>
                <div className={g.realized_pnl >= 0 ? "text-long" : "text-short"}>${g.realized_pnl.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Investment</div>
                <div>${g.investment.toFixed(2)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
        </>
      )}
    </div>
  )
}
