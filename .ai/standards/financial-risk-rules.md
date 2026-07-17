# Financial Risk Rules — Non-negotiable

- Never open a position without confirmed balance > $10.
- Never allow SL to be set below liquidation price.
- Never allow max_open_positions to be summed across exchanges (global cap only).
- Never execute on RSI data that returned 50.0 (fake fallback — abort instead).
- Never bypass OTP confirmation for trade execution via dashboard.
- Carry strategy must be blocked from SELL when 1D RSI < 40.
