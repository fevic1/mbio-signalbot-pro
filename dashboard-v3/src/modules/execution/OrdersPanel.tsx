import { apiFetch } from "@/lib/api"
import { usePollingResource } from "@/hooks/usePollingResource"
import { Badge } from "@/components/ui/badge"

interface OrderRow {
  source: "exchange" | "grid" | "dca"
  asset: string
  side: string
  price: number
  size: number | null
  order_id: string | number | null
  label: string
}

const POLL_INTERVAL_MS = 15_000

export function OrdersPanel() {
  const {
    data: orders,
    loading,
    error,
  } = usePollingResource(
    async () => {
      const res = await apiFetch<{ orders: OrderRow[]; count: number }>("/orders")
      return res.orders
    },
    POLL_INTERVAL_MS
  )

  if (error && !orders) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
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
            <th className="p-3 font-normal">Intent</th>
            <th className="p-3 font-normal">Side</th>
            <th className="p-3 font-normal">Execution</th>
            <th className="p-3 font-normal">Price</th>
            <th className="p-3 font-normal">Size</th>

          </tr>
        </thead>
        <tbody className="font-mono">
          {orders.map((o, i) => (
            <tr key={`${o.order_id ?? i}-${o.source}`} className="border-t border-border">
              <td className="p-3 font-sans font-semibold">
                {o.asset}
              </td>

              <td className="p-3 font-sans text-muted-foreground">
                {o.label}
              </td>

              <td className="p-3">
                <Badge variant={o.side === "BUY" ? "long" : "short"}>
                  {o.side || "—"}
                </Badge>
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
                  ACTIVE
                </span>
              </td>

              <td className="p-3">
                {o.price ? `$${o.price.toLocaleString()}` : "—"}
              </td>

              <td className="p-3">
                {o.size !== null ? o.size : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      </div>
    </div>
  )
}
