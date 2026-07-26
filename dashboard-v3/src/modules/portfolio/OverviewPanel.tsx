import { safeToFixed } from '../../utils/format';
import { useState } from "react"
import { apiFetch } from "@/lib/api"
import { usePollingResource } from "@/hooks/usePollingResource"
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
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const {
    data,
    loading,
    error,
  } = usePollingResource(
    async () => {
      const res = await apiFetch<OverviewData>("/overview")
      setLastUpdated(new Date())
      return res
    },
    POLL_INTERVAL_MS
  )

  if (error && !data) {
    return (
      <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">
        {error}
      </div>
    )
  }

  if (loading || !data) {
    return <p className="text-sm text-muted-foreground">Loading overview…</p>
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-xs text-warn">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      <Card className="
        rounded-2xl
        border-white/10
        bg-white/5
      ">

        <CardHeader className="!justify-between">

          <span className="text-lg font-bold">
            Portfolio State
          </span>

          {lastUpdated && (
            <span className="text-[10px] text-muted-foreground">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}

        </CardHeader>


        <CardContent className="
          grid
          grid-cols-2
          gap-6
          md:grid-cols-4
        ">
          <Stat
            label="Total Capital"
            value={`$${safeToFixed(data?.total_balance)}`}
          />


          <Stat
            label="Equity"
            value={`$${safeToFixed(data?.equity)}`}
          />


          <Stat
            label="Exposure"
            value={`${safeToFixed(data?.deployed_pct,1)}%`}
          />


          <Stat
            label="Notional"
            value={`$${safeToFixed(data?.notional)}`}
          />


          <Stat
            label="Daily Performance"
            value={`${data.daily_pnl_pct >= 0 ? "+" : ""}${safeToFixed(data?.daily_pnl_pct,2)}%`}
            tone={pnlTone(data.daily_pnl_pct)}
          />


          <Stat
            label="Realized PnL"
            value={`$${safeToFixed(data?.realized_pnl_usd)}`}
            tone={pnlTone(data.realized_pnl_usd)}
          />


          <Stat
            label="Unrealized PnL"
            value={`$${safeToFixed(data?.unrealized_pnl_usd)}`}
            tone={pnlTone(data.unrealized_pnl_usd)}
          />


          <Stat
            label="Win Rate"
            value={data.win_rate}
          />
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
