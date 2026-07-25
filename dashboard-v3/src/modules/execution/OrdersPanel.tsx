import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
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

const SOURCE_LABEL: Record<string, string> = {
  exchange: "Exchange",
  grid: "Grid",
  dca: "DCA",
}

export function OrdersPanel() {
  const [orders, setOrders] = useState<OrderRow[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchOrders = useCallback(async () => {
    try {
      const res = await apiFetch<{ orders: OrderRow[]; count: number }>("/orders")
      setOrders(res.orders)
      setError(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load orders")
    }
  }, [])

  useEffect(() => {
    fetchOrders()
    const id = setInterval(fetchOrders, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchOrders])

  if (error && !orders) {
    return <div className="rounded-md border border-short/40 bg-short/10 p-3 text-xs text-short">{error}</div>
  }
  if (!orders) {
    return <p className="text-sm text-muted-foreground">Loading orders…</p>
  }
  if (orders.length === 0) {
    return <p className="text-sm text-muted-foreground">No pending orders.</p>
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
            <th className="pb-2 font-normal">Source</th>
            <th className="pb-2 font-normal">Asset</th>
            <th className="pb-2 font-normal">Type</th>
            <th className="pb-2 font-normal">Side</th>
            <th className="pb-2 font-normal">Price</th>
            <th className="pb-2 font-normal">Size</th>
          </tr>
        </thead>
        <tbody className="font-mono">
          {orders.map((o, i) => (
            <tr key={`${o.order_id ?? i}-${o.source}`} className="border-t border-border">
              <td className="py-2 font-sans text-muted-foreground">{SOURCE_LABEL[o.source] ?? o.source}</td>
              <td className="py-2 font-sans font-semibold">{o.asset}</td>
              <td className="py-2 font-sans text-muted-foreground">{o.label}</td>
              <td className="py-2"><Badge variant={o.side === "BUY" ? "long" : "short"}>{o.side || "—"}</Badge></td>
              <td className="py-2">{o.price ? `$${o.price.toLocaleString()}` : "—"}</td>
              <td className="py-2">{o.size !== null ? o.size : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
