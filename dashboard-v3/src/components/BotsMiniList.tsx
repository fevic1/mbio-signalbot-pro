import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Square } from "lucide-react"

interface Grid {
  key: string
  asset: string
  enabled: boolean
  nodes_active: number
  nodes_total: number
  realized_pnl: number
}

interface DcaPosition {
  asset: string
  direction: string
  filled_levels: number
  levels: number
  total_invested: number
}

const POLL_INTERVAL_MS = 10_000

export function BotsMiniList({
  onCloseGrid,
  onCloseDca,
  refreshKey,
}: {
  onCloseGrid: (asset: string) => void
  onCloseDca: (asset: string) => void
  refreshKey?: number
}) {
  const [grids, setGrids] = useState<Grid[] | null>(null)
  const [dcaPositions, setDcaPositions] = useState<DcaPosition[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchAll = useCallback(async () => {
    try {
      const [g, d] = await Promise.all([
        apiFetch<{ grids: Grid[] }>("/grids"),
        apiFetch<{ positions: DcaPosition[] }>("/dca_status"),
      ])
      setGrids(g.grids)
      setDcaPositions(d.positions)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load bots")
    }
  }, [])

  useEffect(() => {
    fetchAll()
    const id = setInterval(fetchAll, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchAll, refreshKey])

  if (error && !grids && !dcaPositions) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-2 text-xs text-short">{error}</div>
  }
  if (!grids || !dcaPositions) {
    return <p className="text-xs text-muted-foreground">Loading bots…</p>
  }
  if (grids.length === 0 && dcaPositions.length === 0) {
    return <p className="text-xs text-muted-foreground">No active bots.</p>
  }

  return (
    <div className="space-y-1.5">
      {grids.map((g) => (
        <div key={`grid-${g.key}`} className="flex items-center justify-between rounded-md border border-border p-2 text-xs">
          <div className="flex items-center gap-2">
            <Badge variant={g.enabled ? "long" : "default"}>GRID</Badge>
            <span className="font-semibold">{g.asset}</span>
            <span className="font-mono text-muted-foreground">{g.nodes_active}/{g.nodes_total}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={g.realized_pnl >= 0 ? "font-mono text-long" : "font-mono text-short"}>
              ${g.realized_pnl.toFixed(2)}
            </span>
            <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => onCloseGrid(g.asset)} title="Close grid">
              <Square className="h-3 w-3 text-short" />
            </Button>
          </div>
        </div>
      ))}
      {dcaPositions.map((d) => (
        <div key={`dca-${d.asset}`} className="flex items-center justify-between rounded-md border border-border p-2 text-xs">
          <div className="flex items-center gap-2">
            <Badge variant={d.direction === "LONG" ? "long" : "short"}>DCA</Badge>
            <span className="font-semibold">{d.asset}</span>
            <span className="font-mono text-muted-foreground">{d.filled_levels}/{d.levels}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-muted-foreground">${d.total_invested.toFixed(2)}</span>
            <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => onCloseDca(d.asset)} title="Close DCA">
              <Square className="h-3 w-3 text-short" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
