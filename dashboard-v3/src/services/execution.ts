import { apiFetch } from "@/lib/api"

export interface Order {
  order_id: string
  asset: string
  side: string
  order_type: string
  price: number
  quantity: number
  filled: number
  remaining: number
  status: string
  created_at: string
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
  const res = await apiFetch<{ orders: Order[] }>("/orders", { signal })
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
