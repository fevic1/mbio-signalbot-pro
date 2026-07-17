# Architecture

**Repo:** https://github.com/fevic1/mbio-signalbot-pro
**VPS path:** `/root/hyperliquid-agent-scout/`
**Stack:** Python, FastAPI, Docker Compose, Redis, ChromaDB, SQLite, Telegram Bot API, Hyperliquid SDK, Bybit API

## Backend
- FastAPI application, runs in a Docker container.
- Exchanges: Hyperliquid (agent-wallet API) and Bybit.
- Data source: Hyperliquid candle API (yFinance has been fully replaced — confirmed working).

## Frontend
- Migration in progress: rebuild from scratch, workflow-oriented.
- Old artifacts being retired: `frontend-v2-dist/`, `frontend/`.

## Core modules of note
- `core/data_fetcher.py` — market data + balance fetching.
- `core/hip4_metadata.py` — HIP-4 prediction market metadata. Must have a TTL guard (max one refresh per 5 minutes).
- `execution/hl_executor.py` — order placement. Must be a true singleton — never re-initialized per call.
- `routes/dashboard_api.py` — REST contract the new frontend wires against.
