# MBIO + Vibe-Trading Integration Architecture

## Executive Summary
This document outlines the architectural plan to integrate Vibe-Trading AI's quantitative research capabilities (Alpha Zoo, Backtesting, MCP) with MBIO SignalBot Pro's institutional-grade live execution engine.

## 1. Current State vs. Target State
- **Current**: MBIO handles live execution (Hyperliquid/Bybit), Grid/DCA management, and basic RSI/MACD regime detection.
- **Target**: A closed-loop system where Vibe-Trading researches/backtests strategies, and MBIO executes them with strict OTP-gated risk management.

## 2. Core Integration Vectors
### Vector A: MBIO as an MCP Execution Tool (High Priority)
- **Concept**: Expose MBIO's read-only and execution endpoints via Model Context Protocol (MCP).
- **Implementation**: Create `routes/mcp_server.py` using `fastmcp`.
- **Tools Exposed**: 
  - `get_positions`, `get_account_balance` (Read-only)
  - `place_grid`, `place_dca`, `close_position` (Requires OTP confirmation payload)
- **Security**: All execution tools enforce the existing OTP middleware and audit logging.

### Vector B: Import "Alpha Zoo" into MBIO Signal Generator (High Priority)
- **Concept**: Replace simple technical indicators with Vibe-Trading's 461 pre-built alphas (GTJA-191, Qlib, Kakushadze).
- **Implementation**: 
  - Create `core/factors/gtja_191.py` for factor calculations.
  - Create `core/factors/regime_detector.py` to output `TRENDING`, `RANGING`, or `BREAKOUT` based on composite factor scores.
- **Benefit**: Dynamic Grid/DCA parameter optimization based on mathematically robust market regimes.

### Vector C: Unified Dashboard Telemetry (Medium Priority)
- **Concept**: Port Vibe-Trading's "Run Detail" and "Alpha Bench" charting components into `dashboard-v3`.
- **Implementation**: Add `FactorPanel.tsx` and `BacktestResults.tsx` to the existing React 19 + Vite frontend.

## 3. Implementation Phases (5-Week Rollout)
| Phase | Focus Area | Key Deliverables | Risk Mitigation |
|---|---|---|---|
| **Phase 1** | Factor Library | Port GTJA-191 factors, build AST-hardened sandbox. | Unit test all 191 factors against historical data. |
| **Phase 2** | Strategy Optimization | Dynamic grid range & DCA sizing based on factor volatility. | A/B test against current static parameters in paper trading. |
| **Phase 3** | MCP Server Setup | `routes/mcp_server.py`, OTP-gated execution tools, audit trail. | Strict rate limiting and mandatory OTP for all state-changing tools. |
| **Phase 4** | Dashboard Enhancement | React components for factor analytics and backtest visualization. | Ensure WebSocket live-push does not cause UI blinking. |

## 4. Financial Risk Rules (Non-Negotiable)
1. Never open a position without confirmed balance > $10.
2. Never allow SL to be set below liquidation price.
3. Never bypass OTP confirmation for trade execution via dashboard or MCP.
4. Carry strategy must be blocked from SELL when 1D RSI < 40.

## 5. Next Immediate Actions
- [ ] Review and approve this architecture document.
- [ ] Initialize `core/factors/` directory and port the first 10 GTJA factors.
- [ ] Set up `pytest` suite for factor validation.
