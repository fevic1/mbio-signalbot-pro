import { safeToFixed } from '../../utils/format';
import { useEffect } from "react"
import { apiFetch } from "@/lib/api"
import { usePollingResource } from "@/hooks/usePollingResource"
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
  margin_used: number
  liquidation_px: number
  sl: number
  tp1: number
  tp2: number
  tp3: number
  strategy: string
  exchange?: string
  opened_at?: string
}

const POLL_INTERVAL_MS = 10_000

export function PositionsPanel({ 
  onClose, 
  refreshKey 
}: { 
  onClose: (pos: Position) => void, 
  refreshKey?: number 
}) {
  const {
    data: positions,
    loading,
    error,
    refresh: fetchPositions,
  } = usePollingResource(
    async () => {
      const res = await apiFetch<{ positions: Position[]; count: number }>("/positions")
      return res.positions
    },
    POLL_INTERVAL_MS
  )

  useEffect(() => {
    if (refreshKey !== undefined && refreshKey > 0) {
      fetchPositions()
    }
  }, [refreshKey, fetchPositions])

  if (error && !positions) {
    return <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">{error}</div>
  }

  if (loading || !positions) {
    return <p className="text-sm text-muted-foreground">Loading positions…</p>
  }

  if (positions.length === 0) {
    return <p className="text-sm text-muted-foreground">No open positions.</p>
  }

  const portfolioStats = {
    exposure: positions.reduce((sum, p) => sum + p.value, 0),
    pnl: positions.reduce((sum, p) => sum + p.upnl, 0),
    longs: positions.filter((p) => p.side === "BUY").length,
    shorts: positions.filter((p) => p.side !== "BUY").length,
    monitored: positions.filter((p) => p.liquidation_px > 0).length,
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Metric label="Exposure" value={`$${safeToFixed(portfolioStats.exposure)}`} />
        <Metric label="Unrealized PnL" value={`$${safeToFixed(portfolioStats.pnl)}`} />
        <Metric label="Longs" value={String(portfolioStats.longs)} />
        <Metric label="Shorts" value={String(portfolioStats.shorts)} />
        <Metric label="Risk Monitored" value={`${portfolioStats.monitored}/${positions.length}`} />
      </div>

      {error && (
        <div className="rounded-md border border-yellow-500/40 bg-yellow-500/10 p-2 text-xs text-yellow-600 dark:text-yellow-400">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}

      <div className="rounded-xl border border-border overflow-hidden bg-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground">
                <th className="p-3 font-normal">Asset</th>
                <th className="p-3 font-normal">Strategy</th>
                <th className="p-3 font-normal">Side</th>
                <th className="p-3 font-normal">Size</th>
                <th className="p-3 font-normal">Entry</th>
                <th className="p-3 font-normal">Mark</th>
                <th className="p-3 font-normal">PnL (USD / %)</th>
                <th className="p-3 font-normal">Stop Loss</th>
                <th className="p-3 font-normal">Take Profit</th>
                <th className="p-3 font-normal">Liq. Price</th>
                <th className="p-3 font-normal text-right">Action</th>
              </tr>
            </thead>
            <tbody className="font-mono divide-y divide-border">
              {positions.map((p) => (
                <tr key={`${p.exchange}-${p.asset}`} className="hover:bg-muted/30 transition-colors">
                  <td className="p-3 font-sans font-semibold">{p.asset}</td>
                  <td className="p-3 text-muted-foreground text-xs">{p.strategy || "MANUAL"}</td>
                  <td className="p-3">
                    <Badge variant={p.side === "BUY" ? "long" : "short"} className="text-[10px]">
                      {p.side === "BUY" ? "LONG" : "SHORT"}
                    </Badge>
                </td>
                  <td className="p-3">{safeToFixed(p.size)}</td>
                  <td className="p-3">${p.entry.toLocaleString()}</td>
                  <td className="p-3">${p.current.toLocaleString()}</td>
                  <td className={cn("p-3", p.upnl >= 0 ? "text-green-500" : "text-red-500")}>
                    <div>${safeToFixed(p.upnl)}</div>
                    <div className="text-xs">{p.pnl_pct >= 0 ? "+" : ""}{safeToFixed(p.pnl_pct)}%</div>
                  </td>
                  <td className="p-3 text-red-400">
                    {p.sl > 0 ? `$${p.sl.toLocaleString()}` : "—"}
                  </td>
                  <td className="p-3 text-green-400">
                    {p.tp1 > 0 ? `$${p.tp1.toLocaleString()}` : "—"}
                  </td>
                  <td className="p-3 text-yellow-500">
                    {p.liquidation_px > 0 ? `$${p.liquidation_px.toLocaleString()}` : "—"}
                  </td>
                  <td className="p-3 text-right">
                    <Button
                      size="sm"
                      variant="destructive"
                      className="h-7 text-xs"
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
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-muted/20 p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
    </div>
  )
}
