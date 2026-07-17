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
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground">
            <th className="pb-2 font-normal">Exchange</th>
            <th className="pb-2 font-normal">Asset</th>
            <th className="pb-2 font-normal">Side</th>
            <th className="pb-2 font-normal">Size</th>
            <th className="pb-2 font-normal">Entry</th>
            <th className="pb-2 font-normal">Current</th>
            <th className="pb-2 font-normal">uPnL</th>
            <th className="pb-2 font-normal">Liq. Px</th>
            <th className="pb-2 font-normal"></th>
          </tr>
        </thead>
        <tbody className="font-mono">
          {positions.map((p) => (
            <tr key={`${p.exchange}-${p.asset}`} className="border-t border-border">
              <td className="py-2 text-xs font-sans text-muted-foreground">{p.exchange || "Hyperliquid"}</td>
              <td className="py-2 font-sans font-semibold">{p.asset}</td>
              <td className="py-2"><Badge variant={p.side === "BUY" ? "long" : "short"}>{p.side === "BUY" ? "Long" : "Short"}</Badge></td>
              <td className="py-2">{p.size}</td>
              <td className="py-2">${p.entry.toLocaleString()}</td>
              <td className="py-2">${p.current.toLocaleString()}</td>
              <td className={cn("py-2", p.upnl >= 0 ? "text-long" : "text-short")}>
                ${p.upnl.toFixed(2)} ({p.pnl_pct >= 0 ? "+" : ""}{p.pnl_pct.toFixed(2)}%)
              </td>
              <td className="py-2 text-muted-foreground">{p.liquidation_px > 0 ? `$${p.liquidation_px.toLocaleString()}` : "—"}</td>
              <td className="py-2 text-right font-sans">
                <Button size="sm" variant="destructive" onClick={() => onClose(p)}>Close</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
