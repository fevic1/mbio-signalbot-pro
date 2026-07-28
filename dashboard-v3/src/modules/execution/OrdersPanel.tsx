import { getOrders } from "@/services/execution"
import { usePollingResource } from "@/hooks/usePollingResource"
import { Badge } from "@/components/ui/badge"

const POLL_INTERVAL_MS = 15_000

export function OrdersPanel() {
  const {
    data: orders,
    loading,
    error,
  } = usePollingResource(
    (signal) => getOrders(signal),
    POLL_INTERVAL_MS
  )

  if (error && !orders) {
    return <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">{error}</div>
  }
  if (loading || !orders) {
    return <p className="text-sm text-muted-foreground">Loading orders…</p>
  }
  if (orders.length === 0) {
    return <p className="text-sm text-muted-foreground">No pending orders.</p>
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md border border-yellow-500/40 bg-yellow-500/10 p-2 text-xs text-yellow-600 dark:text-yellow-400">
          Last refresh failed: {error} — showing last known values.
        </div>
      )}
      <div className="rounded-xl border border-border overflow-hidden bg-card">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground">
              <th className="p-3 font-normal">Asset</th>
              <th className="p-3 font-normal">Intent</th>
              <th className="p-3 font-normal">Side</th>
              <th className="p-3 font-normal">Execution</th>
              <th className="p-3 font-normal">Price</th>
              <th className="p-3 font-normal">Size</th>
            </tr>
          </thead>
          <tbody className="font-mono divide-y divide-border">
            {orders.map((o, i) => (
              <tr key={`${o.order_id ?? i}-${o.source}`} className="hover:bg-muted/30 transition-colors">
                <td className="p-3 font-sans font-semibold">{o.asset}</td>
                <td className="p-3 font-sans text-muted-foreground">{o.label}</td>
                <td className="p-3">
                  <Badge variant={o.side === "BUY" ? "long" : "short"}>
                    {o.side || "—"}
                  </Badge>
                </td>
                <td className="p-3">
                  <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-1 text-xs font-semibold text-green-500">
                    ACTIVE
                  </span>
                </td>
                <td className="p-3">{o.price ? `$${o.price.toLocaleString()}` : "—"}</td>
                <td className="p-3">{o.size !== null ? o.size : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
