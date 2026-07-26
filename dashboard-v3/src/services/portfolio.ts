import { apiFetch } from "@/lib/api"

export interface PortfolioOverview {
  equity: number
  available_balance: number
  unrealized_pnl: number
  realized_pnl: number
  daily_pnl: number
  margin_used: number
  margin_ratio: number
}

export interface Position {
  asset: string
  side: string
  size: number
  entry_price: number
  mark_price: number
  liquidation_price: number | null
  unrealized_pnl: number
  realized_pnl: number
  leverage: number
  margin: number
}

export async function getOverview(signal?: AbortSignal) {
  return apiFetch<PortfolioOverview>("/overview", { signal })
}

export async function getPositions(signal?: AbortSignal) {
  const res = await apiFetch<{ positions: Position[] }>("/positions", {
    signal,
  })

  return res.positions
}
