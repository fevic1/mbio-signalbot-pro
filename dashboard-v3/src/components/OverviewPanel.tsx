import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface OverviewData {
  hl_balance: number
  bybit_balance: number
  total_balance: number
  balance: number // kept for backward compat
  equity: number
  deployed_pct: number
  notional: number
  open_positions: number
  daily_pnl_pct: number
  realized_pnl_usd: number
  unrealized_pnl_usd: number
  win_rate: string
  total_trades: number
  active_grids: number
}

const POLL_INTERVAL_MS = 10_000

function Stat({ label, value, tone }: { label: string; value: string; tone?: "long" | "short" | "default" }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className={cn(
        "font-mono text-lg font-semibold",
        tone === "long" && "text-long",
        tone === "short" && "text-short"
      )}>
        {value}
      </div>
    </div>
  )
}

function pnlTone(n: number): "long" | "short" | "default" {
  if (n > 0) return "long"
  if (n < 0) return "short"
  return "default"
}

export function OverviewPanel() {
  const [data, setData] = useState<OverviewData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchOverview = useCallback(async () => {
    try {
      const res = await apiFetch<OverviewData>("/overview")
      setData(res)
      setError(null)
      setLastUpdated(new Date())
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load overview")
    }
  }, [])

  useEffect(() => {
    fetchOverview()
    const id = setInterval(fetchOverview, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchOverview])

  if (error && !data) {
    return (
      <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">
        {error}
      </div>
    )
  }

  if (!data) {
    return <p className="text-sm text-muted-foreground">Loading overview…</p>
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-xs text-warn">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      <Card>
        <CardHeader className="!justify-between">
          <span className="text-sm font-semibold">Account</span>
          {lastUpdated && (
            <span className="text-[10px] text-muted-foreground">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Stat label="HL Balance" value={`$${data.hl_balance.toFixed(2)}`} />
          <Stat label="Bybit Balance" value={`$${data.bybit_balance.toFixed(2)}`} />
          <Stat label="Total Balance" value={`$${data.total_balance.toFixed(2)}`} />
          <Stat label="Total Equity" value={`$${data.equity.toFixed(2)}`} />
          <Stat label="Deployed" value={`${data.deployed_pct.toFixed(1)}%`} />
          <Stat label="Notional" value={`$${data.notional.toFixed(2)}`} />
          <Stat label="Daily PnL" value={`${data.daily_pnl_pct >= 0 ? "+" : ""}${data.daily_pnl_pct.toFixed(2)}%`} tone={pnlTone(data.daily_pnl_pct)} />
          <Stat label="Realized" value={`$${data.realized_pnl_usd.toFixed(2)}`} tone={pnlTone(data.realized_pnl_usd)} />
          <Stat label="Unrealized" value={`$${data.unrealized_pnl_usd.toFixed(2)}`} tone={pnlTone(data.unrealized_pnl_usd)} />
          <Stat label="Win Rate" value={data.win_rate} />
        </CardContent>
      </Card>
      <div className="flex gap-3 text-xs text-muted-foreground">
        <span>{data.open_positions} open position{data.open_positions === 1 ? "" : "s"}</span>
        <span>·</span>
        <span>{data.active_grids} active grid{data.active_grids === 1 ? "" : "s"}</span>
        <span>·</span>
        <span>{data.total_trades} total trades</span>
      </div>
    </div>
  )
}
