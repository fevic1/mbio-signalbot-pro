# MBIO SignalBot Pro: API & MCP Tool Reference

## 1. MCP Gateway Endpoints
### `POST /mcp/{server_id}/invoke`
Executes a tool within a specific MCP server namespace.
- **Headers:** `Content-Type: application/json`, `X-API-Key: <server_api_key>`

### `GET /mcp/servers`
Returns a list of all registered MCP servers.

## 2. MCP Tool Specifications
### Server: vibe-trading
- `get_market_regime`: Fetches live GTJA-191 factor analysis. Asset is dynamic.
- `place_grid`: Deploys a grid strategy. Requires OTP. Investment validated against dynamic min/max limits.

### Server: risk-analyzer
- `validate_portfolio_exposure`: Pre-trade safety check against dynamic config limits.
- `check_asset_correlation`: Calculates rolling correlation to prevent hidden concentration.

## 3. Dashboard API Endpoints
- `GET /api/dashboard/mcp/servers`: Lists active MCP servers.
- `POST /api/dashboard/mcp/register`: Registers a new MCP server.
- `POST /api/dashboard/mcp/unregister/{server_id}`: Removes an MCP server.
