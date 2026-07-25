import { safeToFixed } from '../../utils/format';
import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface Position {
  asset: string
  side: string
  size: number
  entry: number
  current: number
  upnl: number
  pnl_pct: number
  value: number
  liquidation_px: number
  sl: number
  tp1: number
  strategy: string
  exchange?: string
}

const POLL_INTERVAL_MS = 10_000

export function PositionsPanel({ onClose, refreshKey }: { onClose: (pos: Position) => void, refreshKey?: number }) {
  const [positions, setPositions] = useState<Position[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchPositions = useCallback(async () => {
    try {
      const res = await apiFetch<{ positions: Position[]; count: number }>("/positions")
      setPositions(res.positions)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load positions")
    }
  }, [])

  useEffect(() => {
    fetchPositions()
    const id = setInterval(fetchPositions, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchPositions])

  // Refresh when refreshKey changes (after close operation)
  useEffect(() => {
    if (refreshKey !== undefined && refreshKey > 0) {
      fetchPositions()
    }
  }, [refreshKey, fetchPositions])

  if (error && !positions) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
  }

  if (!positions) {
    return <p className="text-sm text-muted-foreground">Loading positions…</p>
  }

  if (positions.length === 0) {
    return <p className="text-sm text-muted-foreground">No open positions.</p>
  }

  return (
    <div className="space-y-3">
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

            <th className="p-3 font-normal">Asset</th>
            <th className="p-3 font-normal">Strategy</th>
            <th className="p-3 font-normal">Direction</th>
            <th className="p-3 font-normal">Exposure</th>
            <th className="p-3 font-normal">Entry</th>
            <th className="p-3 font-normal">Market</th>
            <th className="p-3 font-normal">PnL</th>
            <th className="p-3 font-normal">Risk</th>
            <th className="p-3"></th>

          </tr>

        </thead>
        <tbody className="font-mono">
          {positions.map((p) => (
            <tr key={`${p.exchange}-${p.asset}`} className="border-t border-border">
              <td className="p-3 font-sans font-semibold">
                {p.asset}
              </td>


              <td className="p-3 text-muted-foreground">
                {p.strategy || "MANUAL"}
              </td>


              <td className="p-3">
                <Badge variant={p.side === "BUY" ? "long" : "short"}>
                  {p.side === "BUY" ? "LONG" : "SHORT"}
                </Badge>
              </td>


              <td className="p-3">
                ${safeToFixed(p.value)}
              </td>


              <td className="p-3">
                ${p.entry.toLocaleString()}
              </td>


              <td className="p-3">
                ${p.current.toLocaleString()}
              </td>


              <td className={cn(
                "p-3",
                p.upnl >= 0
                  ? "text-long"
                  : "text-short"
              )}>
                ${safeToFixed(p.upnl)}
                <br/>
                <span className="text-xs">
                  {p.pnl_pct >= 0 ? "+" : ""}
                  {safeToFixed(p.pnl_pct)}%
                </span>
              </td>


              <td className="p-3">

                <span className="
                  rounded-full
                  px-2
                  py-1
                  text-xs
                  bg-green-500/10
                  text-green-400
                ">
                  {p.liquidation_px > 0 ? "MONITORED" : "N/A"}
                </span>

              </td>


              <td className="p-3 text-right">

                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => onClose(p)}
                >
                  Close
                </Button>

              </td>
            </tr>
          ))}
        </tbody>
      </table>

      </div>

    </div>
  )
}
