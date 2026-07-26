import { apiFetch } from "@/lib/api"

export interface OrderRow {
  source: "exchange" | "grid" | "dca"
  asset: string
  side: string
  price: number
  size: number | null
  order_id: string | number | null
  label: string
}

export interface ActivityEvent {
  timestamp: string
  event_type: string
  asset: string
  strategy: string
  side: string
  size: number
  price: number
  pnl: number
  order_id: string | null
}

export interface Grid {
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

export async function getOrders(signal?: AbortSignal) {
  const res = await apiFetch<{ orders: OrderRow[]; count: number }>("/orders", { signal })
  return res.orders
}

export async function getActivity(signal?: AbortSignal) {
  const res = await apiFetch<{ activity: ActivityEvent[] }>("/activity", { signal })
  return res.activity
}

export async function getGrids(signal?: AbortSignal) {
  const res = await apiFetch<{ grids: Grid[] }>("/grids", { signal })
  return res.grids
}
