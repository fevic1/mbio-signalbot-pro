# hyperliquid-agent-scout

Modular, institutional-grade AI trading agent for Hyperliquid perpetual futures.

## Features
- **AI-powered** macro bias, scout filter, and risk audit using DeepSeek.
- **Dynamic risk management** with ATR-based stops, 1:3 R:R, partial exits, trailing stops.
- **Modular architecture** – configuration, AI, risk, execution, state, alerts all separated.
- **Persistent state** via JSON file (can be upgraded to Redis).
- **Telegram alerts** for orders and hourly summaries.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your keys.
4. Adjust `config/settings.yaml` if needed.
5. Run: `python main.py`

## Configuration
All parameters are in `config/settings.yaml`.

## State Persistence
The agent saves its state to `state.json` every cycle, enabling crash recovery.
