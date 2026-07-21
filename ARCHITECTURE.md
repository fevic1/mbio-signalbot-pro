# MBIO SignalBot Pro: Institutional Architecture Documentation

## 1. Core Design Principles
- **Zero Hardcoding:** All trading assets, minimum/maximum trade sizes, grid parameters, and risk limits are dynamically resolved. They are **never** hardcoded. Sources include:
  - `config_loader.get_config()` (YAML/ENV-driven risk and execution limits).
  - HIP-4 Exchange API (Dynamic asset universe and metadata).
  - Runtime state (e.g., current account equity for dynamic position sizing).
- **Separation of Concerns:** Strategy logic, risk validation, execution, and MCP routing are strictly isolated into dedicated modules.
- **Security-First Execution:** All state-mutating operations (e.g., `place_grid`) require cryptographic OTP validation via Telegram.

## 2. System Components

### 2.1. Dynamic Strategy Engine (`core/strategy/`)
- **Regime Analyzer:** Computes vectorized GTJA-191 alpha factors over rolling windows. Outputs dynamic regime classifications (TRENDING, RANGING, BREAKOUT) with confidence scores.
- **Grid Manager:** Calculates optimal grid nodes, step sizes, and investment allocations based on the current regime and dynamically loaded risk limits (`min_trade_size`, `max_notional_per_asset`).

### 2.2. Advanced Risk Management (`core/risk_manager.py`)
Intercepts all execution requests to enforce pre-trade safety:
- **Portfolio Exposure Validation:** Checks proposed investments against dynamic `max_notional_per_asset` and `max_open_positions` limits.
- **Asset Correlation Engine:** Fetches rolling 7-day 1H candle data to calculate Pearson correlation between the target asset and existing open positions, flagging hidden concentration risks.

### 2.3. Multi-Tenant MCP Gateway (`core/mcp_registry.py`, `routes/mcp_gateway.py`)
- **Thread-Safe Registry:** Uses `asyncio.Lock` to manage isolated server namespaces (e.g., `vibe-trading`, `risk-analyzer`).
- **Dynamic Tool Binding:** Tools are registered at startup via `core/mcp_tools.py`, mapping JSON-RPC 2.0 requests to internal async functions.
- **Rate Limiting:** Enforced per-server via environment variables (`MCP_*_RATE_LIMIT`).

### 2.4. Execution & State (`core/grid_manager.py`, `core/state.py`)
- Maintains in-memory state for open positions and active grid engines.
- Interfaces with `HLExecutor` for live Hyperliquid order placement, ensuring all sizes respect the dynamically fetched `min_trade_size` for the specific asset.

### 2.5. Institutional Dashboard (`dashboard-v3/`)
- **Reactive UI:** Vite/React frontend with cached backend polling to prevent UI blinking.
- **Dynamic Asset Selection:** All regime and market panels feature dynamic dropdowns populated by the HIP-4 universe, not static lists.
- **MCP Management Console:** Secure, authenticated UI for registering new MCP servers, rotating API keys, and monitoring rate limits.

## 3. Configuration Management
All operational parameters are externalized:
- **`.env`**: API keys, OTP secrets, MCP server credentials, and base rate limits.
- **`config.yaml` (via `config_loader`)**: 
  - `execution.min_trade_size` (Dynamic baseline, overridden by HIP-4 metadata if higher).
  - `execution.max_notional_per_asset`
  - `risk_management.max_open_positions`
  - `risk_management.correlation_warning_threshold`

## 4. Security Model
1. **Read Operations:** Protected by MCP Server API Keys (passed via `X-API-Key` header).
2. **Write/Execution Operations:** Protected by MCP API Key **+** 6-digit Time-based OTP (validated against the user's Telegram session).
3. **Dashboard Operations:** Protected by JWT/Session-based authentication (`get_current_user` dependency).
