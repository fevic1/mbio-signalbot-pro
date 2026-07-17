"""
Server-Sent Events stream for real-time dashboard updates.
"""
import asyncio
import json
import math
import os
import time
import logging
from core.app_context import app_context
from core.app_context import app_context
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
_start_time = time.time()


def _compute_analytics_snapshot() -> dict:
    snapshot = {"total_trades": 0, "win_rate": 0, "total_pnl": 0, "profit_factor": 0,
                "sharpe_ratio": 0, "max_drawdown_pct": 0, "equity_curve": []}
    try:
        with open("data/trade_history.json", "r") as f:
            trades = json.load(f)
    except Exception:
        return snapshot
    if not trades:
        return snapshot
    pnls = [float(t.get("pnl", t.get("realized_pnl", 0))) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    snapshot["total_trades"] = len(pnls)
    snapshot["win_rate"] = round(len(wins) / len(pnls) * 100, 1) if pnls else 0
    snapshot["total_pnl"] = round(sum(pnls), 2)
    gp = sum(wins) if wins else 0
    gl = abs(sum(losses)) if losses else 0
    snapshot["profit_factor"] = round(gp / gl, 2) if gl > 0 else (999.99 if gp > 0 else 0)
    if len(pnls) > 1:
        mean_pnl = sum(pnls) / len(pnls)
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / (len(pnls) - 1)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        snapshot["sharpe_ratio"] = round(mean_pnl / std_dev * math.sqrt(252), 2) if std_dev > 0 else 0
    equity = 0; peak = 0; max_dd_pct = 0; curve = []
    for i, p in enumerate(pnls):
        equity += p; peak = max(peak, equity)
        dd_pct = ((peak - equity) / peak * 100) if peak > 0 else 0
        max_dd_pct = max(max_dd_pct, dd_pct)
        curve.append(round(equity, 2))
    snapshot["max_drawdown_pct"] = round(max_dd_pct, 2)
    snapshot["equity_curve"] = curve[-100:]
    return snapshot


def _collect_system_metrics() -> dict:
    metrics = {"tasks": {}, "uptime_sec": int(time.time() - _start_time),
               "auto_trading": os.environ.get("ENABLE_AUTO_TRADING", "false").lower() == "true",
               "last_update": datetime.now(timezone.utc).isoformat()}
    known_tasks = ["position_monitor", "quick_scanner", "entry_scanner", "full_analysis",
                   "slot_hunter", "trailing_dca", "profit_target_monitor", "grid_monitor"]
    try:
        import core.state as state
        task_states = getattr(state, 'BACKGROUND_TASKS', {})
        for name in known_tasks:
            ts = task_states.get(name, {})
            last_run = ts.get("last_run", "")
            error_count = ts.get("error_count", 0)
            status = "healthy"
            if last_run:
                try:
                    last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - last_dt).total_seconds()
                    if age > 600: status = "stale"
                except Exception: status = "unknown"
            else: status = "not_started"
            if error_count > 5: status = "degraded"
            metrics["tasks"][name] = {"status": status, "last_run": last_run, "error_count": error_count}
    except Exception:
        for name in known_tasks:
            metrics["tasks"][name] = {"status": "unknown", "last_run": "", "error_count": 0}
    return metrics


async def _collect_dashboard_state() -> dict:
    state_data = {"timestamp": datetime.now(timezone.utc).isoformat(), "balance": 0.0, "equity": 0.0,
                  "deployed_pct": 0.0, "positions": [], "grids": [], "analytics": {},
                  "safety_limits": {}, "system": {}}
    try:
        import core.state as state
        from config_loader import get_config
        cfg = get_config()
        try:
            from core.data_fetcher import get_account_balance
            state_data["balance"] = round(get_account_balance(), 2)
        except Exception: pass
        try:
            from core.app_context import app_context
            executor = app_context.executor
            mids = executor.info.all_mids()
            exchange_positions = {}
            try:
                raw = executor.info.user_state(executor.address)
                for ap in raw.get("assetPositions", []):
                    pos = ap.get("position", {}); coin = pos.get("coin", "")
                    if coin:
                        exchange_positions[coin] = {
                            "margin_used": float(pos.get("marginUsed", 0)),
                            "liquidation_px": float(pos.get("liquidationPx", 0)),
                            "leverage": float(pos.get("leverage", {}).get("value", 1)),
                            "roe": float(pos.get("returnOnEquity", 0))}
            except Exception as e: logger.debug(f"SSE exchange fetch: {e}")
            for key, pos in state.OPEN_POSITIONS.items():
                if key.startswith("GRID::"): continue
                asset = key; side = pos.get("side", "BUY"); size = float(pos.get("size", 0))
                entry = float(pos.get("entry", 0)); current = float(mids.get(asset, 0))
                upnl = ((current - entry) * size if side == "BUY" else (entry - current) * size) if current > 0 else 0
                pnl_pct = (((current - entry) / entry * 100) if side == "BUY" else ((entry - current) / entry * 100)) if entry > 0 else 0
                exch = exchange_positions.get(asset, {})
                state_data["positions"].append({
                    "asset": asset, "side": side, "size": round(size, 8),
                    "entry": round(entry, 4), "current": round(current, 4), "upnl": round(upnl, 4),
                    "pnl_pct": round(pnl_pct, 2),
                    "margin_used": round(exch.get("margin_used", float(pos.get("margin_used", 0))), 4),
                    "liquidation_px": round(exch.get("liquidation_px", float(pos.get("liquidation_px", 0))), 2),
                    "leverage": round(exch.get("leverage", 1), 1), "roe": round(exch.get("roe", 0) * 100, 2),
                    "sl": round(float(pos.get("sl", 0)), 4), "tp1": round(float(pos.get("tp1", 0)), 4),
                    "tp2": round(float(pos.get("tp2", 0)), 4), "tp3": round(float(pos.get("tp3", 0)), 4),
                    "strategy": pos.get("strategy", "UNKNOWN"), "opened_at": str(pos.get("opened_at", ""))})
            total_upnl = sum(p["upnl"] for p in state_data["positions"])
            state_data["equity"] = round(state_data["balance"] + total_upnl, 2)
            total_notional = sum(p["size"] * p["current"] for p in state_data["positions"] if p["current"] > 0)
            state_data["deployed_pct"] = round(total_notional / state_data["balance"] * 100, 1) if state_data["balance"] > 0 else 0.0
        except Exception as e: logger.debug(f"SSE position fetch: {e}")
        try:
            from core.grid_manager import is_grid_position, grid_asset_from_key
            for key, config in state.OPEN_POSITIONS.items():
                if not is_grid_position(key): continue
                asset = grid_asset_from_key(key); nodes = config.get("nodes", [])
                active = len([n for n in nodes if n.get("status") == "OPEN"])
                state_data["grids"].append({
                    "asset": asset, "mode": config.get("mode", "RANGE"),
                    "lower_price": round(float(config.get("lower_price", 0)), 2),
                    "upper_price": round(float(config.get("upper_price", 0)), 2),
                    "step_size": round(float(config.get("step_size", 0)), 2),
                    "nodes_active": active, "nodes_total": len(nodes),
                    "cycles": config.get("completed_cycles", 0),
                    "realized_pnl": round(float(config.get("total_realized_pnl", 0)), 4),
                    "investment": round(float(config.get("investment_amount", 0)), 2)})
        except Exception as e: logger.debug(f"SSE grid fetch: {e}")
        try: state_data["analytics"] = _compute_analytics_snapshot()
        except Exception: pass
        try:
            risk_cfg = cfg.get("risk", {})
            state_data["safety_limits"] = {
                "max_positions": int(risk_cfg.get("max_positions", 5)),
                "min_notional": float(risk_cfg.get("min_notional", 2)),
                "max_leverage": int(risk_cfg.get("max_leverage", 20)),
                "max_notional_per_asset": float(risk_cfg.get("max_notional_per_asset", 100))}
        except Exception: pass
        try: state_data["system"] = _collect_system_metrics()
        except Exception: pass
    except Exception as e: logger.error(f"SSE state collection error: {e}")
    return state_data


async def sse_generator(request: Request = None):
    while True:
        try:
            if request:
                from routes.dashboard_auth import get_current_user
                try:
                    user = get_current_user(request)
                except Exception:
                    err_payload = json.dumps({"error": "unauthenticated", "balance": 0, "equity": 0})
                    yield f"data: {err_payload}\n\n"
                    await asyncio.sleep(5)
                    continue
            data = await _collect_dashboard_state()
            payload = json.dumps(data, default=str)
            yield f"data: {payload}\n\n"
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"SSE generator error: {e}")
            err_payload = json.dumps({"error": str(e)})
            yield f"data: {err_payload}\n\n"
        await asyncio.sleep(2)


async def dashboard_sse_stream(request: Request = None):
    return StreamingResponse(sse_generator(request), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})
