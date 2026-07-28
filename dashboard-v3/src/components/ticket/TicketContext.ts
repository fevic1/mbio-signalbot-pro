export type TicketContext =
  | { type: "edit_bot"; coin: string }
  | { type: "close_position"; asset: string; side: string; size: number }
  | { type: "close_grid"; asset: string }
  | { type: "open_grid" }
  | { type: "close_dca"; asset: string }
  | { type: "quick_trade"; asset: string; side?: "BUY" | "SELL" }
  | { type: "open_dca" }
  | { type: "create_bot_choice" }
  | { type: "quick" }
  | null
