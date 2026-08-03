
# Hyperliquid MCP

Status: TESTING

Version: 1.0.0

Backend:
execution.hl_executor

Read-only
-----------
✓ hl_market_info
✓ hl_all_mids
✓ hl_orderbook
✓ hl_candles
✓ hl_funding
✓ hl_open_orders
✓ hl_positions
✓ hl_balances

Execution
---------
✓ hl_place_order
✓ hl_cancel_order

This MCP wraps the existing execution layer.
No duplicate trading logic exists.
