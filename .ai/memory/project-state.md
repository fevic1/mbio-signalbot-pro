# Project State

**Last updated:** 2026-07-18
**Current Bot State:**
- Balance: ~$11.44 on Hyperliquid (Master wallet address verified).
- Auto Trading: ENABLED (`ENABLE_AUTO_TRADING=true`).
- Grid running: ETH (1 cycle, +$0.23 PnL), BTC (0 cycles) - *Needs re-verification*.
- Dashboard migration: In progress (Step 1: sse.js extraction).
- yFinance replaced with HL candle API — confirmed working.

**Active Issues:**
1. Duplicate `grid_monitor` task — still running twice (needs code audit).
2. ChromaDB Telemetry error: `capture() takes 1 positional argument but 3 were given` (low priority, log pollution).
3. Groq API rate limit near/at cap (429 errors observed).
4. Missing `timeout` on some `requests.post` calls in `core/data_fetcher.py`, `core/hip4_metadata.py`, `execution/hl_executor.py`.
