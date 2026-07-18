"""
Dashboard API routes v4 - Institutional-grade with session auth + RBAC.
Phase 4: Config editor (structured), audit viewer, signal reconciliation.
All config from strategy_config.yaml. Manual reload after save.
"""
import time
import json
import math
import shutil
import logging
import yaml
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional, List

from routes.dashboard_auth import (
    get_current_user, require_role, verify_otp_for_user,
    login, logout, request_otp, get_me, log_audit
)
from routes.dashboard_sse import dashboard_sse_stream
from core.app_context import app_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_start_time = time.time()

CONFIG_PATH = "config/strategy_config.yaml"
CONFIG_BACKUP_PATH = "config/strategy_config.yaml.bak"


# --- Auth Routes ---

router.post("/auth/login")(login)
router.post("/auth/logout")(logout)
router.get("/auth/me")(get_me)
router.post("/auth/otp/request")(request_otp)


# ============================================================
# CONFIG MANAGEMENT (Structured form, ADMIN-only, OTP-gated)
# ============================================================


def calculate_market_regime(prices: list) -> str:
    """
    Calculate market regime based on price action.
    Returns: "TRENDING", "RANGING", or "BREAKOUT"
    """
    if not prices or len(prices) < 20:
        return "RANGING"
    
    # Calculate ADX-like trend strength
    highs = [float(p.get("h", 0)) for p in prices[-20:]]
    lows = [float(p.get("l", 0)) for p in prices[-20:]]
    closes = [float(p.get("c", 0)) for p in prices[-20:]]
    
    # Calculate price range
    price_range = max(highs) - min(lows)
    avg_price = sum(closes) / len(closes)
    range_pct = (price_range / avg_price) * 100 if avg_price > 0 else 0
    
    # Calculate trend direction
    first_half_avg = sum(closes[:10]) / 10 if len(closes) >= 20 else closes[0]
    second_half_avg = sum(closes[10:]) / len(closes[10:]) if len(closes) >= 20 else closes[-1]
    trend_strength = abs(second_half_avg - first_half_avg) / first_half_avg * 100 if first_half_avg > 0 else 0
    
    # Determine regime
    if trend_strength > 3:  # Strong directional movement
        return "TRENDING"
    elif range_pct > 5:  # High volatility, potential breakout
        return "BREAKOUT"
    else:  # Low volatility, sideways
        return "RANGING"

@router.get("/config/current")
async def get_current_config(user: dict = Depends(require_role("ADMIN"))):
    """Return current YAML config as structured JSON for form pre-fill."""
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = yaml.safe_load(f) or {}
        return {"config": cfg, "path": CONFIG_PATH}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {str(e)[:200]}")


@router.post("/config/save")
async def save_config(request: Request, user: dict = Depends(require_role("ADMIN"))):
    """Save structured config. Creates backup, validates YAML, requires OTP."""
    body = await request.json()
    _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"

    new_config = body.get("config", {})
    if not isinstance(new_config, dict):
        raise HTTPException(status_code=400, detail="Config must be a JSON object")

    # Validate YAML serialization before writing
    try:
        yaml_str = yaml.dump(new_config, default_flow_style=False, sort_keys=False)
        yaml.safe_load(yaml_str)  # Round-trip validation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config structure: {str(e)[:200]}")

    # Create backup
    try:
        if os.path.exists(CONFIG_PATH):
            shutil.copy2(CONFIG_PATH, CONFIG_BACKUP_PATH)
    except Exception as e:
        logger.error(f"Config backup failed: {e}")

    # Write new config
    try:
        with open(CONFIG_PATH, "w") as f:
            f.write(yaml_str)
        log_audit(user["id"], "CONFIG_SAVE", resource=CONFIG_PATH,
                  details=json.dumps({"sections": list(new_config.keys())})[:1000],
                  ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": "Config saved. Click 'Apply Changes' to activate.", "backup": CONFIG_BACKUP_PATH}
    except Exception as e:
        log_audit(user["id"], "CONFIG_SAVE_FAILED", resource=CONFIG_PATH,
                  details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Config save failed: {str(e)[:200]}")


@router.post("/config/reload")
async def reload_config(request: Request, user: dict = Depends(require_role("ADMIN"))):
    """Hot-reload YAML config without container restart. Requires OTP."""
    body = await request.json()
    _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"

    try:
        from config_loader import get_config, _load_config
        # Force re-read from disk
        if hasattr(_load_config, '__globals__'):
            _load_config.__globals__.pop('_cached_config', None)
        # Try common cache-clearing patterns
        import config_loader
        if hasattr(config_loader, '_cached_config'):
            config_loader._cached_config = None
        if hasattr(config_loader, '_config_cache'):
            config_loader._config_cache = None

        # Verify reload worked
        cfg = get_config()
        log_audit(user["id"], "CONFIG_RELOAD", resource=CONFIG_PATH,
                  details=json.dumps({"sections": list(cfg.keys()) if cfg else []}),
                  ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": "Config reloaded successfully. New settings active."}
    except Exception as e:
        log_audit(user["id"], "CONFIG_RELOAD_FAILED", resource=CONFIG_PATH,
                  details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Config reload failed: {str(e)[:200]}. Bot may need restart.")


# ============================================================
# AUDIT LOG VIEWER (ADMIN-only, 90-day retention)
# ============================================================

@router.get("/audit-log")
async def get_audit_log(
    user: dict = Depends(require_role("ADMIN")),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    action: str = Query(default="", description="Filter by action type"),
    user_id: str = Query(default="", description="Filter by user ID"),
    search: str = Query(default="", description="Search in resource/details"),
):
    """Searchable audit log with filters. 90-day retention."""
    try:
        from db.dashboard_models import get_dashboard_db
        conn = get_dashboard_db()

        # Build query with filters
        conditions = ["created_at > datetime('now', '-90 days')"]
        params = []
        if action:
            conditions.append("action LIKE ?")
            params.append(f"%{action}%")
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if search:
            conditions.append("(resource LIKE ? OR details LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT * FROM dashboard_audit_log WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) as cnt FROM dashboard_audit_log WHERE {where}", params
        ).fetchone()["cnt"]
        conn.close()

        return {
            "entries": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Audit log query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audit log query failed: {str(e)[:200]}")


# ============================================================
# SIGNAL RECONCILIATION (Auto-detect + manual clear)
# ============================================================

@router.get("/signals/orphaned")
async def get_orphaned_signals(user: dict = Depends(get_current_user)):
    """Auto-detect signals in DB that have no matching exchange position."""
    orphaned = []
    try:
        import core.state as state
        import sqlite3

        # Get current exchange position assets
        active_assets = set()
        for key in state.OPEN_POSITIONS.keys():
            if not key.startswith("GRID::"):
                active_assets.add(key.upper())

        # Find closed signals still marked OPEN in DB
        conn = sqlite3.connect("data/signals.db")
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM signals WHERE status = 'OPEN' ORDER BY timestamp DESC"
        ).fetchall()
        conn.close()

        for r in rows:
            r = dict(r)
            asset = r.get("asset", "").upper()
            if asset and asset not in active_assets:
                orphaned.append({
                    "id": r.get("id"),
                    "asset": asset,
                    "signal": r.get("signal", ""),
                    "entry_price": float(r.get("entry_price", 0)),
                    "timestamp": r.get("timestamp", ""),
                    "reason": "No matching exchange position",
                })
    except Exception as e:
        logger.error(f"Orphan detection failed: {e}")

    return {"orphaned": orphaned, "count": len(orphaned)}


@router.post("/signals/reconcile")
async def reconcile_signals(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    """Manually close selected orphaned signals. Requires OTP."""
    body = await request.json()
    _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"

    signal_ids = body.get("signal_ids", [])
    if not signal_ids:
        raise HTTPException(status_code=400, detail="No signal IDs provided")

    closed = 0
    errors = []
    try:
        import sqlite3
        conn = sqlite3.connect("data/signals.db")
        for sid in signal_ids:
            try:
                conn.execute(
                    "UPDATE signals SET status = 'CLOSED', closed_at = ? WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), sid)
                )
                closed += 1
            except Exception as e:
                errors.append(f"Signal {sid}: {str(e)[:100]}")
        conn.commit()
        conn.close()
    except Exception as e:
        errors.append(f"DB error: {str(e)[:200]}")

    log_audit(user["id"], "SIGNAL_RECONCILE", resource=f"{closed} signals",
              details=json.dumps({"closed": closed, "errors": errors[:10]}),
              ip_address=ip, otp_verified=True)

    return {"status": "ok", "closed": closed, "errors": errors}


# ============================================================
# EXISTING ENDPOINTS (Phase 2-3 preserved)
# ============================================================

def _validate_otp_or_raise(user: dict, otp: str):
    if not otp or not verify_otp_for_user(user["email"], otp):
        raise HTTPException(status_code=403, detail="Invalid or expired OTP")


def _get_risk_limits() -> dict:
    try:
        from config_loader import get_config
        cfg = get_config()
        risk = cfg.get("risk", {})
        return {
            "max_positions": int(risk.get("max_positions", 5)),
            "min_notional": float(risk.get("min_notional", 2)),
            "max_leverage": int(risk.get("max_leverage", 20)),
        }
    except Exception:
        return {"max_positions": 5, "min_notional": 2, "max_leverage": 20}


@router.get("/config/defaults")
async def get_config_defaults(user: dict = Depends(get_current_user)):
    defaults = {"grid": {}, "dca": {}, "risk": {}}
    try:
        from config_loader import get_config
        cfg = get_config()
        grid_cfg = cfg.get("grid", {})
        defaults["grid"] = {
            "investment_amount": float(grid_cfg.get("investment_amount", 30)),
            "num_nodes": int(grid_cfg.get("num_nodes", 10)),
            "mode": str(grid_cfg.get("mode", "RANGE")),
            "min_step_size": float(grid_cfg.get("min_step_size", 0.5)),
            "max_range_pct": float(grid_cfg.get("max_range_pct", 10)),
        }
        dca_cfg = cfg.get("dca", {})
        defaults["dca"] = {
            "base_order_size": float(dca_cfg.get("base_order_size", 5)),
            "max_safety_orders": int(dca_cfg.get("max_safety_orders", 5)),
            "price_deviation_pct": float(dca_cfg.get("price_deviation_pct", 1.5)),
            "safety_order_step_scale": float(dca_cfg.get("safety_order_step_scale", 1.2)),
            "take_profit_pct": float(dca_cfg.get("take_profit_pct", 1.5)),
            "stop_loss_pct": float(dca_cfg.get("stop_loss_pct", 5)),
        }
        risk_cfg = cfg.get("risk", {})
        defaults["risk"] = {
            "max_positions": int(risk_cfg.get("max_positions", 5)),
            "max_notional_per_asset": float(risk_cfg.get("max_notional_per_asset", 100)),
            "min_notional": float(risk_cfg.get("min_notional", 2)),
            "max_leverage": int(risk_cfg.get("max_leverage", 20)),
        }
    except Exception as e:
        logger.error(f"Failed to load config defaults: {e}")
    return defaults


@router.get("/config/assets")
async def get_config_assets(user: dict = Depends(get_current_user)):
    assets = []
    try:
        from config_loader import get_config
        cfg = get_config()
        raw_assets = cfg.get("grid", {}).get("assets", None)
        if not raw_assets:
            assets_cfg = cfg.get("assets", {})
            if isinstance(assets_cfg, dict):
                for category, symbols in assets_cfg.items():
                    if isinstance(symbols, dict):
                        raw_assets = list(symbols.keys())
                        break
                    elif isinstance(symbols, list):
                        raw_assets = symbols
                        break
            elif isinstance(assets_cfg, list):
                raw_assets = assets_cfg
        if not raw_assets:
            pairs_cfg = cfg.get("pairs", {})
            if isinstance(pairs_cfg, dict):
                raw_assets = list(pairs_cfg.keys())
            elif isinstance(pairs_cfg, list):
                raw_assets = pairs_cfg
        if not raw_assets:
            raw_assets = ["BTC", "ETH", "HYPE"]
        for a in raw_assets:
            if isinstance(a, dict):
                assets.append({"symbol": a.get("symbol", a.get("asset", "")).upper(), "name": a.get("name", a.get("symbol", ""))})
            else:
                assets.append({"symbol": str(a).upper(), "name": str(a).upper()})
    except Exception as e:
        logger.error(f"Failed to load assets: {e}")
        assets = [{"symbol": "BTC"}, {"symbol": "ETH"}, {"symbol": "HYPE"}]
    return {"assets": assets}


@router.get("/health")
async def dashboard_health(user: dict = Depends(get_current_user)):
    checks = {"telegram_bot": False, "config_loaded": False, "exchange_connected": False, "grid_state_loaded": False}
    try:
        import sys; am = sys.modules.get('monitoring.alert_manager')
        checks["telegram_bot"] = bool(am and hasattr(am, '_application'))
    except Exception: pass
    try:
        from config_loader import get_config; checks["config_loaded"] = bool(get_config())
    except Exception: pass
    try:
        from execution.hl_executor import hl_executor; checks["exchange_connected"] = bool(hl_executor.info.all_mids())
    except Exception: pass
    try:
        import core.state as state; checks["grid_state_loaded"] = len(state.OPEN_POSITIONS) >= 0
    except Exception: pass
    return {"status": "ok" if all(checks.values()) else "degraded", "checks": checks, "uptime_sec": int(time.time() - _start_time)}


@router.get("/overview")
async def dashboard_overview(user: dict = Depends(get_current_user)):
    result = {"hl_balance": 0.0, "bybit_balance": 0.0, "total_balance": 0.0, 
              "equity": 0.0, "deployed_pct": 0.0, "notional": 0.0, "open_positions": 0,
              "daily_pnl_pct": 0.0, "realized_pnl_usd": 0.0, "unrealized_pnl_usd": 0.0,
              "win_rate": "N/A", "total_trades": 0, "active_grids": 0}
    
    # 1. Hyperliquid Balance
    try:
        from core.data_fetcher import get_account_balance
        result["hl_balance"] = round(get_account_balance(), 2)
    except Exception: pass
    
    # 2. Bybit Balance
    try:
        from execution.bybit_executor import get_bybit_executor
        bybit_ex = get_bybit_executor()
        if bybit_ex and bybit_ex.client:
            res = bybit_ex.client.get_wallet_balance(accountType="UNIFIED")
            if res["retCode"] == 0:
                result["bybit_balance"] = round(float(res["result"]["list"][0]["totalEquity"]), 2)
    except Exception: pass
    
    result["total_balance"] = round(result["hl_balance"] + result["bybit_balance"], 2)
    result["balance"] = result["total_balance"] # Backward compatibility
    try:
        import core.state as state
        from core.grid_manager import is_grid_position
        positions = {k: v for k, v in state.OPEN_POSITIONS.items() if not is_grid_position(k)}
        grids = {k: v for k, v in state.OPEN_POSITIONS.items() if is_grid_position(k)}
        result["open_positions"] = len(positions); result["active_grids"] = len(grids)
        notional = sum(float(p.get("size", 0)) * float(p.get("entry", 0)) for p in positions.values())
        result["notional"] = round(notional, 2)
        result["deployed_pct"] = round((notional / result["balance"] * 100) if result["balance"] > 0 else 0, 1)
    except Exception: pass
    try:
        from core.performance_tracker import get_performance_tracker
        tracker = get_performance_tracker(); stats = tracker.get_performance_stats({})
        result["realized_pnl_usd"] = round(stats.get("realized_pnl_usd", 0), 2)
        result["unrealized_pnl_usd"] = round(stats.get("unrealized_pnl_usd", 0), 2)
        result["daily_pnl_pct"] = round(stats.get("realized_pnl_pct", 0) + stats.get("unrealized_pnl_pct", 0), 2)
        result["total_trades"] = stats.get("closed_trades", 0)
        if stats.get("closed_trades", 0) > 0: result["win_rate"] = f"{stats['win_rate']:.1f}%"
    except Exception: pass
    result["equity"] = round(result["total_balance"] + result["unrealized_pnl_usd"], 2)
    return result


def _json_safe_float(value, default=0.0, cap=10_000_000.0):
    """Clamp inf/-inf/NaN to a finite value — json.dumps() cannot serialize any of
    these and will 500 the entire endpoint if one slips through. Applies regardless
    of how the bad value got into state.OPEN_POSITIONS in the first place."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(f):
        return default
    if math.isinf(f):
        return cap if f > 0 else -cap
    return f


@router.get("/positions")
async def dashboard_positions(user: dict = Depends(get_current_user)):
    positions = []
    try:
        import core.state as state
        # _get_executor replaced by app_context
        from core.grid_manager import is_grid_position
        executor = app_context.executor; mids = executor.info.all_mids()
        for key, pos in state.OPEN_POSITIONS.items():
            if is_grid_position(key): continue
            asset = key; side = pos.get("side", "BUY"); size = float(pos.get("size", 0))
            entry = float(pos.get("entry", 0)); current = float(mids.get(asset, 0))
            upnl = ((current - entry) * size if side == "BUY" else (entry - current) * size) if current > 0 else 0
            pnl_pct = (((current - entry) / entry * 100) if side == "BUY" else ((entry - current) / entry * 100)) if entry > 0 else 0
            positions.append({"asset": asset, "side": side, "size": round(size, 8), "entry": round(entry, 4),
                              "current": round(current, 4), "upnl": round(upnl, 4), "pnl_pct": round(pnl_pct, 2),
                              "value": round(size * current, 2), "margin_used": round(float(pos.get("margin_used", 0)), 4),
                              "liquidation_px": round(float(pos.get("liquidation_px", 0)), 2),
                              "sl": round(_json_safe_float(pos.get("sl", 0)), 4), "tp1": round(_json_safe_float(pos.get("tp1", 0)), 4),
                              "tp2": round(_json_safe_float(pos.get("tp2", 0)), 4), "tp3": round(_json_safe_float(pos.get("tp3", 0)), 4),
                              "strategy": pos.get("strategy", "UNKNOWN"), "opened_at": str(pos.get("opened_at", "")),
                              "exchange": "Hyperliquid"})
    except Exception as e: logger.error(f"Positions fetch error: {e}")
    
    # Fetch Bybit Positions
    try:
        from execution.bybit_executor import get_bybit_executor
        bybit_ex = get_bybit_executor()
        if bybit_ex and bybit_ex.client:
            bybit_positions = bybit_ex.get_open_positions()
            for p in bybit_positions:
                side = "BUY" if p["side"] == "long" else "SELL"
                size = p["size"]
                entry = p["entry_price"]
                current = float(mids.get(p["coin"], entry)) # Fallback to entry if mid missing
                upnl = ((current - entry) * size if side == "BUY" else (entry - current) * size) if current > 0 else 0
                pnl_pct = (((current - entry) / entry * 100) if side == "BUY" else ((entry - current) / entry * 100)) if entry > 0 else 0
                positions.append({
                    "asset": p["coin"], "side": side, "size": round(size, 8), "entry": round(entry, 4),
                    "current": round(current, 4), "upnl": round(upnl, 4), "pnl_pct": round(pnl_pct, 2),
                    "value": round(size * current, 2), "margin_used": 0.0, "liquidation_px": 0.0,
                    "sl": 0.0, "tp1": 0.0, "tp2": 0.0, "tp3": 0.0,
                    "strategy": "BYBIT", "opened_at": "", "exchange": "Bybit"
                })
    except Exception as e: 
        logger.error(f"Bybit positions fetch error: {e}")
        
    return {"positions": positions, "count": len(positions)}


@router.get("/grids")
async def dashboard_grids(user: dict = Depends(get_current_user)):
    grids = []
    try:
        import core.state as state
        from core.grid_manager import is_grid_position, grid_asset_from_key
        for key, config in state.OPEN_POSITIONS.items():
            if not is_grid_position(key): continue
            if not config.get("enabled", False): continue  # skip closed grids — was showing "Inactive" zombie cards forever
            asset = grid_asset_from_key(key); nodes = config.get("nodes", [])
            active = len([n for n in nodes if n.get("status") == "OPEN"])
            grids.append({"key": key, "asset": asset, "enabled": config.get("enabled", False),
                          "mode": config.get("mode", "RANGE"),
                          "lower_price": round(float(config.get("lower_price", 0)), 2),
                          "upper_price": round(float(config.get("upper_price", 0)), 2),
                          "step_size": round(float(config.get("step_size", 0)), 2),
                          "grid_quantity": config.get("grid_quantity", len(nodes)),
                          "nodes_active": active, "nodes_total": len(nodes),
                          "cycles": config.get("completed_cycles", 0),
                          "realized_pnl": round(float(config.get("total_realized_pnl", 0)), 4),
                          "investment": round(float(config.get("investment_amount", 0)), 2),
                          "created_at": str(config.get("created_at", ""))})
    except Exception as e: logger.error(f"Grids fetch error: {e}")
    return {"grids": grids, "count": len(grids)}


@router.get("/stream")
async def dashboard_stream(request: Request):
    """SSE stream - authentication handled internally by generator."""
    return await dashboard_sse_stream(request)


@router.get("/trade-history")
async def get_trade_history(user: dict = Depends(get_current_user), limit: int = 100, offset: int = 0):
    trades = []
    try:
        with open("data/trade_history.json", "r") as f:
            json_trades = json.load(f)
        for t in json_trades:
            trades.append({"id": t.get("id", ""), "asset": t.get("asset", t.get("coin", "")),
                           "side": t.get("side", ""), "entry": float(t.get("entry", t.get("entry_price", 0))),
                           "exit": float(t.get("exit", t.get("exit_price", 0))), "size": float(t.get("size", 0)),
                           "pnl": float(t.get("pnl", t.get("realized_pnl", 0))), "pnl_pct": float(t.get("pnl_pct", 0)),
                           "strategy": t.get("strategy", "MANUAL"), "opened_at": t.get("opened_at", t.get("timestamp", "")),
                           "closed_at": t.get("closed_at", ""), "source": "json"})
    except Exception as e: logger.debug(f"trade_history.json: {e}")
    try:
        import sqlite3
        conn = sqlite3.connect("data/signals.db"); conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM signals WHERE status = 'CLOSED' ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        for r in rows:
            r = dict(r)
            trades.append({"id": str(r.get("id", "")), "asset": r.get("asset", ""), "side": r.get("signal", ""),
                           "entry": float(r.get("entry_price", 0)), "exit": float(r.get("exit_price", 0)),
                           "size": 0, "pnl": 0, "pnl_pct": 0, "strategy": "SIGNAL",
                           "opened_at": r.get("timestamp", ""), "closed_at": r.get("closed_at", ""),
                           "tp_hit": r.get("tp_hit", ""), "source": "db"})
        conn.close()
    except Exception as e: logger.debug(f"signals.db: {e}")
    seen = set(); unique = []
    for t in sorted(trades, key=lambda x: x.get("opened_at", ""), reverse=True):
        key = t.get("id", f"{t['asset']}_{t['opened_at']}")
        if key not in seen: seen.add(key); unique.append(t)
    return {"trades": unique[:limit], "total": len(unique)}


@router.get("/analytics")
async def get_analytics(user: dict = Depends(get_current_user)):
    result = {"total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0, "avg_pnl": 0,
              "best_trade": 0, "worst_trade": 0, "profit_factor": 0, "sharpe_ratio": 0,
              "max_drawdown": 0, "max_drawdown_pct": 0, "equity_curve": [], "monthly_returns": {}}
    try:
        with open("data/trade_history.json", "r") as f: trades = json.load(f)
    except Exception: trades = []
    if not trades: return result
    pnls = [float(t.get("pnl", t.get("realized_pnl", 0))) for t in trades]
    wins = [p for p in pnls if p > 0]; losses = [p for p in pnls if p <= 0]
    result["total_trades"] = len(pnls); result["wins"] = len(wins); result["losses"] = len(losses)
    result["win_rate"] = round(len(wins) / len(pnls) * 100, 1) if pnls else 0
    result["total_pnl"] = round(sum(pnls), 2)
    result["avg_pnl"] = round(sum(pnls) / len(pnls), 2) if pnls else 0
    result["best_trade"] = round(max(pnls), 2) if pnls else 0
    result["worst_trade"] = round(min(pnls), 2) if pnls else 0
    gross_profit = sum(wins) if wins else 0; gross_loss = abs(sum(losses)) if losses else 0
    result["profit_factor"] = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (999.99 if gross_profit > 0 else 0)
    if len(pnls) > 1:
        mean_pnl = sum(pnls) / len(pnls)
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / (len(pnls) - 1)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        result["sharpe_ratio"] = round(mean_pnl / std_dev * math.sqrt(252), 2) if std_dev > 0 else 0
    equity = 0; peak = 0; max_dd = 0; max_dd_pct = 0; curve = []
    for i, p in enumerate(pnls):
        equity += p; peak = max(peak, equity)
        dd = peak - equity; dd_pct = (dd / peak * 100) if peak > 0 else 0
        max_dd = max(max_dd, dd); max_dd_pct = max(max_dd_pct, dd_pct)
        curve.append({"trade": i + 1, "equity": round(equity, 2)})
    result["max_drawdown"] = round(max_dd, 2); result["max_drawdown_pct"] = round(max_dd_pct, 2)
    result["equity_curve"] = curve[-200:]
    monthly = {}
    for t in trades:
        ts = t.get("closed_at", t.get("timestamp", ""))
        if ts and len(ts) >= 7:
            month = ts[:7]; pnl = float(t.get("pnl", t.get("realized_pnl", 0)))
            monthly[month] = round(monthly.get(month, 0) + pnl, 2)
    result["monthly_returns"] = dict(sorted(monthly.items()))
    return result


# --- Grid/DCA/Order Write Endpoints (Phase 2-3 preserved) ---


@router.get("/dca_status")
async def dashboard_dca_status(user: dict = Depends(get_current_user)):
    """Real DCA position status, read from the same persisted state open_dca_position()
    and close_dca_position() write to — no separate/ephemeral DCA store."""
    dca_positions = []
    try:
        import core.state as state
        for asset, pos in state.OPEN_POSITIONS.items():
            if asset.startswith("GRID::"):
                continue
            dca = pos.get("dca")
            if not dca:
                continue
            active_count = len([o for o in dca.get("active_orders", []) if o.get("status") == "active"])
            dca_positions.append({
                "asset": asset,
                "direction": dca.get("direction", pos.get("side", "")),
                "levels": dca.get("levels", 0),
                "filled_levels": len(dca.get("filled_levels", [])),
                "active_orders": active_count,
                "base_size": dca.get("base_size", 0),
                "total_invested": dca.get("total_invested", 0.0),
                "avg_entry": dca.get("avg_entry", pos.get("entry", 0)),
                "entry": pos.get("entry", 0),
                "enabled": dca.get("enabled", False),
                # 🛡️ VISIBILITY: Expose TP/SL to end user dashboard
                "sl": pos.get("sl", 0),
                "tp1": pos.get("tp1", 0),
                "tp2": pos.get("tp2", 0),
                "tp3": pos.get("tp3", 0),
            })
    except Exception as e:
        logger.error(f"DCA status fetch error: {e}")

    return {"positions": dca_positions, "count": len(dca_positions)}


@router.get("/orders")
async def dashboard_orders(user: dict = Depends(get_current_user)):
    """Merged view of resting orders: real exchange limit orders + pending grid nodes + pending DCA levels."""
    orders = []

    # 1. Real resting limit orders sitting on the exchange order book
    try:
        executor = app_context.executor
        # SDK BUG WORKAROUND: open_orders sometimes returns empty if address formatting is strict.
        # We log the address to verify, and attempt the call.
        logger.debug(f"Fetching open orders for address: {executor.address}")
        raw_orders = executor.info.open_orders(executor.address)
        
        if not raw_orders:
            logger.warning("⚠️ SDK open_orders returned empty. This is a known SDK version issue. Relying on internal state.")
        else:
            for o in raw_orders:
                orders.append({
                    "source": "exchange",
                    "asset": o.get("coin", ""),
                    "side": "BUY" if o.get("side") == "B" else "SELL",
                    "price": float(o.get("limitPx", 0)),
                    "size": float(o.get("sz", 0)),
                    "order_id": o.get("oid"),
                    "label": "Limit Order",
                })
    except Exception as e:
        logger.error(f"Exchange open orders fetch error: {e}")

    # 2. Grid nodes waiting to fill (not yet executed on the exchange)
    try:
        import core.state as state
        for key, pos in state.OPEN_POSITIONS.items():
            if not key.startswith("GRID::"):
                continue
            for node in pos.get("nodes", []):
                if node.get("status") == "OPEN" and node.get("order_id"):
                    orders.append({
                        "source": "grid",
                        "asset": key.replace("GRID::", ""),
                        "side": node.get("side", ""),
                        "price": node.get("price", 0),
                        "size": None,
                        "order_id": node.get("order_id"),
                        "label": f"Grid L{node.get('level_index', '?')}",
                    })
    except Exception as e:
        logger.error(f"Grid orders fetch error: {e}")

    # 3. DCA levels waiting to fill
    try:
        import core.state as state
        for asset, pos in state.OPEN_POSITIONS.items():
            if asset.startswith("GRID::"):
                continue
            dca_config = pos.get("dca")
            if not dca_config:
                continue
            for order in dca_config.get("active_orders", []):
                if order.get("status") == "active" and order.get("order_id"):
                    orders.append({
                        "source": "dca",
                        "asset": asset,
                        "side": dca_config.get("direction", pos.get("side", "")),
                        "price": order.get("price", 0),
                        "size": order.get("size", None),
                        "order_id": order.get("order_id"),
                        "label": "DCA Level",
                    })
    except Exception as e:
        logger.error(f"DCA orders fetch error: {e}")

    return {"orders": orders, "count": len(orders)}


@router.get("/activity")
async def dashboard_activity(user: dict = Depends(get_current_user), limit: int = 50):
    """Recent trade/fill activity from the persistent ledger (real executed events, not pre-trade signals)."""
    try:
        from core.trade_ledger import load_history
        history = load_history()
        recent = list(reversed(history))[:limit]
        return {"activity": recent, "count": len(recent)}
    except Exception as e:
        logger.error(f"Activity fetch error: {e}")
        return {"activity": [], "count": 0}


@router.get("/price/{asset}")
async def get_asset_price(asset: str, user: dict = Depends(get_current_user)):
    """Return current mid price for an asset."""
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        mids = executor.info.all_mids()
        price = float(mids.get(asset.upper(), 0))
        if price <= 0:
            raise HTTPException(status_code=404, detail=f"No price available for {asset}")
        return {"asset": asset.upper(), "price": price}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.post("/grid/open")
async def grid_open(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper(); lower = float(body.get("lower_price", 0))
    upper = float(body.get("upper_price", 0)); investment = float(body.get("investment_amount", 0))
    num_nodes = int(body.get("num_nodes", 10))
    if not asset or lower <= 0 or upper <= lower or investment <= 0:
        raise HTTPException(status_code=400, detail="Invalid grid parameters")
    try:
        limits = _get_risk_limits(); import core.state as state
        from core.grid_manager import is_grid_position
        current_grids = sum(1 for k in state.OPEN_POSITIONS if is_grid_position(k))
        if current_grids >= limits["max_positions"]:
            raise HTTPException(status_code=400, detail=f"Max grid positions ({limits['max_positions']}) reached")
    except HTTPException: raise
    except Exception as e: logger.warning(f"Position limit check: {e}")
    try:
        from core.grid_manager import GridManager, grid_state_key; gm = GridManager(app_context.executor)
        result = gm.create_grid(asset=asset, lower_price=lower, upper_price=upper, investment_amount=investment, grid_quantity=num_nodes)
        # Register in global state and persist to disk so the monitor can pick it up
        state.OPEN_POSITIONS[grid_state_key(asset)] = result
        state.save_state()
        log_audit(user["id"], "GRID_OPEN", resource=asset, details=json.dumps({"lower": lower, "upper": upper, "investment": investment, "nodes": num_nodes}), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Grid opened for {asset}", "result": result}
    except Exception as e:
        log_audit(user["id"], "GRID_OPEN_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Grid open failed: {str(e)[:200]}")


@router.post("/grid/close")
async def grid_close(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"; asset = body.get("asset", "").upper()
    if not asset: raise HTTPException(status_code=400, detail="Asset required")
    try:
        from core.grid_manager import GridManager, grid_state_key
        import core.state as state
        gm = GridManager(app_context.executor)
        config = state.OPEN_POSITIONS.get(grid_state_key(asset))
        if not config:
            raise HTTPException(status_code=400, detail=f"No active grid for {asset}")
        result = gm.close_grid(asset=asset, config=config)
        state.save_state()  # Persist enabled=False to prevent grid from reappearing
        log_audit(user["id"], "GRID_CLOSE", resource=asset, details=json.dumps(result, default=str)[:500], ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Grid closed for {asset}", "result": result}
    except Exception as e:
        log_audit(user["id"], "GRID_CLOSE_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Grid close failed: {str(e)[:200]}")


@router.post("/dca/open")
async def dca_open(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    """Calls the SAME shared open_dca_position() the Telegram /open_dca command uses —
    do not reimplement DCA-open logic here. Two separate implementations is exactly
    the class of bug that made DCA silently non-functional before tonight's fix."""
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper()
    raw_side = body.get("side", "BUY").upper()
    # open_dca_position speaks LONG/SHORT (matches Telegram's vocabulary); normalize here.
    side = "LONG" if raw_side in ("BUY", "LONG") else "SHORT"
    if not asset:
        raise HTTPException(status_code=400, detail="Asset required")
    try:
        import main as _main
        from core.dca_lifecycle import open_dca_position
        result = await open_dca_position(asset, side, _main.dca_strategy)
        if not result.get("success"):
            log_audit(user["id"], "DCA_OPEN_FAILED", resource=asset, details=str(result.get("error"))[:500], ip_address=ip, otp_verified=True)
            raise HTTPException(status_code=400, detail=result.get("error", "DCA open failed"))
        log_audit(user["id"], "DCA_OPEN", resource=asset, details=json.dumps({"side": side, "result": result})[:1000], ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": result.get("message", f"DCA opened for {asset} {side}"), "result": result}
    except HTTPException:
        raise
    except Exception as e:
        log_audit(user["id"], "DCA_OPEN_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"DCA open failed: {str(e)[:200]}")


@router.post("/dca/close")
async def dca_close(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"; asset = body.get("asset", "").upper()
    if not asset: raise HTTPException(status_code=400, detail="Asset required")
    try:
        import core.state as state
        position = state.OPEN_POSITIONS.get(asset)
        if not position:
            raise HTTPException(status_code=404, detail=f"No open position for {asset}")
        dca_config = position.get("dca", {})
        position_side = position.get("side", "BUY").upper()
        close_side = "SELL" if position_side in ("BUY", "LONG") else "BUY"

        from core.dca_manager import DCAManager
        dm = DCAManager(app_context.executor)
        result = await dm.close_dca_position(asset=asset, config=dca_config, close_side=close_side)

        if result.get("errors"):
            log_audit(user["id"], "DCA_CLOSE_PARTIAL", resource=asset, details=json.dumps(result, default=str)[:500], ip_address=ip, otp_verified=True)
        else:
            log_audit(user["id"], "DCA_CLOSE", resource=asset, details=json.dumps(result, default=str)[:500], ip_address=ip, otp_verified=True)

        if result.get("base_closed"):
            state.OPEN_POSITIONS.pop(asset, None)
            state.save_state()

        return {"status": "ok", "message": f"DCA closed for {asset}", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        log_audit(user["id"], "DCA_CLOSE_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"DCA close failed: {str(e)[:200]}")


@router.post("/order/market")
async def order_market(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper(); side = body.get("side", "BUY").upper(); size = float(body.get("size", 0))
    if not asset or side not in ("BUY", "SELL") or size <= 0:
        raise HTTPException(status_code=400, detail="Invalid order parameters")
    limits = _get_risk_limits()
    if size * float(body.get("price", 0)) < limits["min_notional"]:
        raise HTTPException(status_code=400, detail=f"Notional below minimum ${limits['min_notional']}")
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        result = executor.market_order(asset, side, size)
        log_audit(user["id"], "ORDER_MARKET", resource=asset, details=json.dumps({"side": side, "size": size}), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Market {side} {size} {asset} executed", "result": result}
    except Exception as e:
        log_audit(user["id"], "ORDER_MARKET_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Market order failed: {str(e)[:200]}")


@router.post("/order/limit")
async def order_limit(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper(); side = body.get("side", "BUY").upper()
    size = float(body.get("size", 0)); price = float(body.get("price", 0))
    if not asset or side not in ("BUY", "SELL") or size <= 0 or price <= 0:
        raise HTTPException(status_code=400, detail="Invalid limit order parameters")
    if size * price < _get_risk_limits()["min_notional"]:
        raise HTTPException(status_code=400, detail=f"Notional below minimum")
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        result = executor.limit_order(asset, side, size, price)
        log_audit(user["id"], "ORDER_LIMIT", resource=asset, details=json.dumps({"side": side, "size": size, "price": price}), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Limit {side} {size} {asset} @ ${price} placed", "result": result}
    except Exception as e:
        log_audit(user["id"], "ORDER_LIMIT_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Limit order failed: {str(e)[:200]}")


@router.post("/order/stop-limit")
async def order_stop_limit(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper(); side = body.get("side", "BUY").upper()
    size = float(body.get("size", 0)); stop_price = float(body.get("stop_price", 0)); limit_price = float(body.get("limit_price", 0))
    if not asset or side not in ("BUY", "SELL") or size <= 0 or stop_price <= 0 or limit_price <= 0:
        raise HTTPException(status_code=400, detail="Invalid stop-limit parameters")
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        result = executor.stop_limit_order(asset, side, size, stop_price, limit_price)
        log_audit(user["id"], "ORDER_STOP_LIMIT", resource=asset, details=json.dumps({"side": side, "size": size, "stop": stop_price, "limit": limit_price}), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Stop-limit {side} {size} {asset} placed", "result": result}
    except Exception as e:
        log_audit(user["id"], "ORDER_STOP_LIMIT_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Stop-limit failed: {str(e)[:200]}")


@router.post("/order/trailing-stop")
async def order_trailing_stop(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"
    asset = body.get("asset", "").upper(); side = body.get("side", "SELL").upper()
    size = float(body.get("size", 0)); trail_pct = float(body.get("trail_pct", 1.0))
    if not asset or size <= 0 or trail_pct <= 0:
        raise HTTPException(status_code=400, detail="Invalid trailing stop parameters")
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        result = executor.trailing_stop_order(asset, side, size, trail_pct)
        log_audit(user["id"], "ORDER_TRAILING_STOP", resource=asset, details=json.dumps({"side": side, "size": size, "trail_pct": trail_pct}), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": f"Trailing stop {side} {size} {asset} ({trail_pct}%) placed", "result": result}
    except Exception as e:
        log_audit(user["id"], "ORDER_TRAILING_STOP_FAILED", resource=asset, details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Trailing stop failed: {str(e)[:200]}")




# ============================================================
# SYSTEM MONITORING (Phase 5)
# ============================================================

@router.get("/system/status")
async def get_system_status(user: dict = Depends(get_current_user)):
    """Background task health matrix: status, last-run, error count."""
    import os
    import time
    from datetime import datetime, timezone

    known_tasks = [
        "position_monitor", "quick_scanner", "entry_scanner",
        "full_analysis", "slot_hunter", "trailing_dca",
        "profit_target_monitor", "grid_monitor",
    ]
    tasks = []
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
                    if age > 600:
                        status = "stale"
                except Exception:
                    status = "unknown"
            else:
                status = "not_started"
            if error_count > 5:
                status = "degraded"
            tasks.append({"id": name, "name": name, "status": status, "last_run": last_run, "error_count": error_count})
    except Exception as e:
        logger.error(f"System status fetch: {e}")
        for name in known_tasks:
            tasks.append({"id": name, "name": name, "status": "unknown", "last_run": "", "error_count": 0})

    return {
        "tasks": tasks,
        "auto_trading": os.environ.get("ENABLE_AUTO_TRADING", "false").lower() == "true",
        "uptime_sec": int(time.time() - _start_time),
    }

# ============================================================
# ALERT CONFIGURATION (Phase 5: Master toggle + group filters)
# ============================================================

ALERT_CONFIG_PATH = "config/alert_preferences.json"

def _load_alert_config() -> dict:
    """Load alert preferences. Returns defaults if file missing."""
    defaults = {
        "master_enabled": True,
        "groups": {
            "trades_fills": True,
            "errors_exceptions": True,
            "routine_scans": False,
        }
    }
    try:
        with open(ALERT_CONFIG_PATH, "r") as f:
            saved = json.load(f)
        # Merge with defaults for forward compatibility
        for k, v in defaults.items():
            if k not in saved:
                saved[k] = v
        if "groups" in saved:
            for gk, gv in defaults["groups"].items():
                if gk not in saved["groups"]:
                    saved["groups"][gk] = gv
        return saved
    except Exception:
        return defaults


@router.get("/alerts/config")
async def get_alerts_config(user: dict = Depends(get_current_user)):
    """Read current alert preferences (master toggle + group filters)."""
    return _load_alert_config()


@router.post("/alerts/config")
async def save_alerts_config(request: Request, user: dict = Depends(require_role("ADMIN"))):
    """Save alert preferences. ADMIN-only + OTP."""
    body = await request.json()
    _validate_otp_or_raise(user, body.get("otp", ""))
    ip = request.client.host if request.client else "unknown"

    config = {
        "master_enabled": bool(body.get("master_enabled", True)),
        "groups": {
            "trades_fills": bool(body.get("trades_fills", True)),
            "errors_exceptions": bool(body.get("errors_exceptions", True)),
            "routine_scans": bool(body.get("routine_scans", False)),
        }
    }

    try:
        with open(ALERT_CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        log_audit(user["id"], "ALERT_CONFIG_SAVE", resource=ALERT_CONFIG_PATH,
                  details=json.dumps(config), ip_address=ip, otp_verified=True)
        return {"status": "ok", "message": "Alert preferences saved", "config": config}
    except Exception as e:
        log_audit(user["id"], "ALERT_CONFIG_SAVE_FAILED", resource=ALERT_CONFIG_PATH,
                  details=str(e)[:500], ip_address=ip, otp_verified=True)
        raise HTTPException(status_code=500, detail=f"Alert config save failed: {str(e)[:200]}")


@router.post("/emergency-stop")
async def emergency_stop(request: Request, user: dict = Depends(require_role("ADMIN"))):
    body = await request.json(); _validate_otp_or_raise(user, body.get("otp", ""))
    if not body.get("confirm"):
        raise HTTPException(status_code=400, detail="Emergency stop requires explicit confirmation")
    ip = request.client.host if request.client else "unknown"
    log_audit(user["id"], "EMERGENCY_STOP_INITIATED", ip_address=ip, otp_verified=True)
    results = {"cancelled_orders": 0, "closed_positions": 0, "errors": []}
    try:
        # _get_executor replaced by app_context
        executor = app_context.executor
        try:
            open_orders = executor.info.open_orders(executor.address)
            for order in open_orders:
                try: executor.cancel_order(order["order"]["oid"]); results["cancelled_orders"] += 1
                except Exception as e: results["errors"].append(f"Cancel: {str(e)[:100]}")
        except Exception as e: results["errors"].append(f"Fetch orders: {str(e)[:100]}")
        try:
            import core.state as state
            for asset in list(state.OPEN_POSITIONS.keys()):
                if asset.startswith("GRID::"): continue
                try:
                    pos = state.OPEN_POSITIONS[asset]; side = pos.get("side", "BUY"); size = float(pos.get("size", 0))
                    if size > 0:
                        close_side = "SELL" if side == "BUY" else "BUY"
                        executor.market_order(asset, close_side, size); results["closed_positions"] += 1
                except Exception as e: results["errors"].append(f"Close {asset}: {str(e)[:100]}")
        except Exception as e: results["errors"].append(f"Positions: {str(e)[:100]}")
    except Exception as e: results["errors"].append(f"Executor: {str(e)[:100]}")
    log_audit(user["id"], "EMERGENCY_STOP_COMPLETED", details=json.dumps(results, default=str)[:1000], ip_address=ip, otp_verified=True)
    return {"status": "ok", "message": f"Emergency stop: {results['cancelled_orders']} cancelled, {results['closed_positions']} closed", "results": results}

# ============================================================
# 2FA Security Setup Endpoints
# ============================================================

@router.get("/security/2fa/setup")
async def get_2fa_setup(user: dict = Depends(require_role("ADMIN"))):
    """Generate OTP secret and QR code URI for 2FA setup."""
    try:
        import pyotp
        from routes.dashboard_auth import get_user_otp_secret, setup_user_otp, generate_otp_qr_uri
        
        email = user.get('email')
        secret = get_user_otp_secret(email)
        
        if not secret:
            secret = setup_user_otp(email)
            
        qr_uri = generate_otp_qr_uri(email, secret)
        
        return {
            "status": "success",
            "secret": secret,
            "qr_uri": qr_uri,
            "is_enabled": bool(secret)
        }
    except Exception as e:
        logger.error(f"2FA setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/security/2fa/verify")
async def verify_2fa_setup(payload: dict, user: dict = Depends(require_role("ADMIN"))):
    """Verify the 6-digit OTP code to finalize 2FA activation."""
    try:
        from routes.dashboard_auth import verify_otp_for_user
        
        otp_code = str(payload.get("otp_code", "")).strip()
        if not otp_code:
            raise HTTPException(status_code=400, detail="OTP code is required")
            
        is_valid = verify_otp_for_user(user["id"], otp_code)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid OTP code. Please check your authenticator app.")
            
        return {"status": "success", "message": "2FA successfully activated!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# MANUAL ORDER EXECUTION (Dashboard Workflow)
# ============================================================

@router.post("/open_order")
async def open_order(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    """
    Execute a manual trade from the dashboard.
    Enforces: OTP confirmation, Balance > $10 guard, and SL validation.
    """
    try:
        # Parse JSON with proper error handling
        import json as json_module
        raw_body = await request.body()
        try:
            body = json_module.loads(raw_body)
        except json_module.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
        
        # 1. SECURITY: Enforce OTP (LLM Instruction: Never bypass OTP)
        _validate_otp_or_raise(user, str(body.get("otp", "")))
        
        # 2. PARSE INPUTS
        asset = str(body.get("asset", "")).strip().upper()
        side = str(body.get("side", "BUY")).strip().upper()
        order_type = str(body.get("type", "market")).strip().lower()
        size_usd = float(body.get("size_usd", 0))
        sl = float(body.get("sl", 0)) if body.get("sl") else None
        tp = float(body.get("tp", 0)) if body.get("tp") else None
        
        if not asset or size_usd <= 0:
            raise HTTPException(status_code=400, detail="Invalid asset or size")
            
        if side not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Side must be BUY or SELL")

        # 3. FINANCIAL RISK GUARD: Balance Check (LLM Instruction: > $10)
        from core.data_fetcher import get_account_balance, get_current_price
        current_balance = get_account_balance()
        if current_balance < 10.0:
            raise HTTPException(status_code=400, detail=f"Insufficient balance (${current_balance:.2f}). Minimum $10 required.")

        # 4. CONVERT USD SIZE TO COIN SIZE
        current_price = get_current_price(asset)
        if current_price <= 0:
            raise HTTPException(status_code=400, detail=f"Cannot fetch price for {asset}")
            
        size_coin = size_usd / current_price
        
        # 4.1 FINANCIAL RISK GUARD: Minimum Notional Check
        min_notional = 10.0  # Hyperliquid minimum
        if size_coin * current_price < min_notional:
            raise HTTPException(
                status_code=400,
                detail=f"Order size ${size_usd:.2f} is below Hyperliquid minimum ${min_notional:.2f}. Increase size."
            )
        
        # 5. EXECUTE VIA EXISTING ENGINE (No core code changes)
        from execution.hl_executor import execute_hl_order
        
        limit_px = None
        if order_type == "limit":
            limit_px = float(body.get("limit_px", 0))
            if limit_px <= 0:
                raise HTTPException(status_code=400, detail="Limit orders require a valid limit_px")
            
        result = execute_hl_order(
            coin=asset,
            side=side,
            size=size_coin,
            limit_px=limit_px,
            sl=sl,
            tp=tp
        )

        # 5.1 UPDATE IN-MEMORY POSITION STATE — without this, the position exists on the
        # exchange but is invisible to the dashboard, Telegram, and (critically) the bot's
        # own check_and_close_positions() SL/TP monitoring, which only reads state.OPEN_POSITIONS.
        if result and result.get("success"):
            import core.state as _state
            from datetime import datetime, timezone
            fill_price = float(result.get("avg_price") or current_price)
            from core.trade_ledger import record_trade
            record_trade("open", asset, "DASHBOARD_UNIFIED", side, size_coin, fill_price,
                          order_id=result.get("order_id"))
            _state.OPEN_POSITIONS[asset] = {
                "side": side,
                "entry": fill_price,
                "size": size_coin,
                # BUY: unset tp1/2/3 must be unreachable upward → float("inf"), confirmed
                # against `if current_price >= pos.get("tp3", float("inf")):` in
                # monitoring/position_tracker.py. Using 0 previously caused an instant false
                # TP3 close on the first live test trade.
                # SELL: no confirmed TP-trigger branch exists in check_and_close_positions —
                # using 0 as a safe non-triggering default until that logic is verified.
                # NOTE: float("inf") is NOT JSON-serializable and will 500 the entire
                # /positions endpoint the moment this position is fetched. Using a large
                # finite number instead — high enough that no real BTC/ETH/etc. price will
                # ever reach it, but still a valid JSON number.
                "sl": sl if sl else 0,
                "tp1": tp if tp else (10_000_000 if side == "BUY" else 0),
                "tp2": tp if tp else (10_000_000 if side == "BUY" else 0),
                "tp3": tp if tp else (10_000_000 if side == "BUY" else 0),
                "order_id": result.get("order_id", "unknown"),
                "opened_at": datetime.now(timezone.utc),
                "strategy": "DASHBOARD_UNIFIED",
            }
            _state.save_state()
            logger.info(f"📊 Position tracked in memory: {asset} {side} @ ${fill_price} (SL: {sl}, TP: {tp})")

        # 6. LOG ACTION
        ip = request.client.host if request.client else "unknown"
        log_audit(
            user["id"], "MANUAL_ORDER", 
            resource=asset, 
            details=json.dumps({"side": side, "size_usd": size_usd, "size_coin": size_coin, "type": order_type, "result": str(result)}), 
            ip_address=ip, 
            otp_verified=True
        )
        
        return {"status": "success", "message": f"Order executed for {asset}", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard order execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])



# ============================================================
# DYNAMIC ASSET CATEGORIZATION (HIP-4)
# ============================================================

@router.get("/assets/categorized")
async def get_categorized_assets(user: dict = Depends(get_current_user)):
    """Return assets dynamically grouped by PERP, SPOT, and TRENDING."""
    try:
        from core.asset_universe import get_universe
        universe = get_universe()
        categories = universe.get_categorized_assets()
        return {"status": "success", "data": categories}
    except Exception as e:
        logger.error(f"Failed to fetch categorized assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================
# HIP-4 ASSET UNIVERSE ENDPOINT (with exchange toggle)
# ============================================================

# ========================================================================
# LIVE ASSET UNIVERSE PIPELINE (Dynamic Exchange Mirror)
# ========================================================================
# Fetches the complete, live list of tradable assets from the exchange.
# No hardcoded lists. No manual categorization. Mirrors the exchange exactly.
# ========================================================================

@router.get("/assets/universe")
async def get_live_universe():
    """
    Fetches the live universe of assets directly from Hyperliquid Info API.
    Uses a SINGLE API call to prevent rate limiting.
    """
    try:
        import requests
        API_URL = "https://api.hyperliquid.xyz/info"
        
        # 1. Single, optimized call for both metadata and live context
        resp = requests.post(API_URL, json={"type": "metaAndAssetCtxs"}, timeout=15)
        if resp.status_code != 200:
            return {"success": False, "error": f"Failed to fetch market data: {resp.status_code}", "assets": []}
        
        data = resp.json()
        if isinstance(data, list) and len(data) >= 2:
            universe_list = data[0].get("universe", [])
            context_list = data[1]
        elif isinstance(data, dict):
            universe_list = data.get("universe", [])
            context_list = data.get("assetCtxs", [])
        else:
            universe_list = []
            context_list = []
            
        live_assets = []
        for idx, asset in enumerate(universe_list):
            ctx = context_list[idx] if idx < len(context_list) else {}
            name = asset.get("name", "UNKNOWN")
            
            # Get price
            price_raw = ctx.get("markPx") or ctx.get("price") or 0
            price = float(price_raw) if price_raw is not None else 0.0
            
            # Calculate 24h change
            prev_px_raw = ctx.get('prevDayPx') or 0
            prev_px = float(prev_px_raw) if prev_px_raw is not None else 0.0
            change_24h = ((price - prev_px) / prev_px * 100) if prev_px > 0 else 0.0
            
            # Get volume and funding
            day_vol_raw = ctx.get("dayNtlVlm") or 0
            day_vol = float(day_vol_raw) if day_vol_raw is not None else 0.0
            
            funding_raw = ctx.get("funding") or 0
            funding = float(funding_raw) if funding_raw is not None else 0.0
            
            # Native Hyperliquid CDN avatar URL
            logo_url = f"https://static.hyperliquid.xyz/token-images/{name.lower()}.png"
            
            # Calculate regime based on 24h change (No extra API calls = No rate limits!)
            abs_change = abs(change_24h)
            if abs_change > 5.0:
                regime = "BREAKOUT"
            elif abs_change > 2.0:
                regime = "TRENDING"
            else:
                regime = "RANGING"
            
            live_assets.append({
                "symbol": name,
                "name": name,
                "logo_url": logo_url,
                "category": "Perp",
                "price": round(price, 4),
                "volume_24h": round(day_vol, 2),
                "change_24h": round(change_24h, 2),
                "funding_rate": funding,
                "max_leverage": asset.get("maxLeverage", 20),
                "sz_decimals": asset.get("szDecimals", 4),
                "type": "PERP",
                "regime": regime,
                "sparkline": [] # Left empty to prevent API rate limits
            })
            
        # Sort by Volume descending
        live_assets.sort(key=lambda x: x["volume_24h"], reverse=True)
        
        return {"success": True, "count": len(live_assets), "assets": live_assets}
        
    except Exception as e:
        logger.error(f"Live Universe Pipeline Error: {e}")
        return {"success": False, "error": str(e), "assets": []}


@router.post("/terminal/candles")
async def get_candles_terminal(request: Request, user: dict = Depends(get_current_user)):
    """
    Fetch candle data from Hyperliquid using existing data_fetcher.
    POST body: {"coin": "BTC", "interval": "15m"}
    """
    try:
        body = await request.json()
        coin = body.get("coin", "BTC")
        interval = body.get("interval", "1h")
        
        # Use the existing working candle fetcher
        from core.data_fetcher import _fetch_hl_candles
        
        # Map interval to lookback days
        interval_days = {
            "1m": 1,
            "5m": 3,
            "15m": 7,
            "30m": 14,
            "1h": 30,
            "4h": 60,
            "1d": 365
        }
        lookback = interval_days.get(interval, 30)
        
        # Fetch candles using existing function
        candles = _fetch_hl_candles(coin.upper(), interval, lookback)
        
        if not candles:
            return []
        
        # Return raw HL format - frontend handles transformation
        return candles
        
    except Exception as e:
        logger.error(f"Candle fetch error: {e}")
        return []


def _interval_to_ms(interval: str) -> int:
    """Convert interval to milliseconds."""
    intervals = {
        "1m": 60000,
        "5m": 300000,
        "15m": 900000,
        "30m": 1800000,
        "1h": 3600000,
        "4h": 14400000,
        "1d": 86400000
    }
    return intervals.get(interval, 3600000)


# ============================================================
# TERMINAL DATA ENDPOINT (for chart widget)
# ============================================================

@router.get("/terminal/data")
async def get_terminal_data(user: dict = Depends(get_current_user)):
    """Return categorized assets and current prices for chart widget."""
    try:
        from core.asset_universe import get_universe
        
        universe = get_universe()
        categories = universe.get_categorized_assets()
        
        # Fetch current prices for trending assets
        prices = {}
        for asset in categories["TRENDING"][:10]:
            try:
                # Use existing price endpoint
                import requests
                r = requests.post(
                    "https://api.hyperliquid.xyz/info",
                    json={"type": "allMids"},
                    timeout=5
                )
                if r.status_code == 200:
                    all_mids = r.json()
                    prices = {k: float(v) for k, v in all_mids.items()}
                    break
            except Exception:
                continue
        
        return {
            "categories": categories,
            "prices": prices,
            "trending": categories["TRENDING"]
        }
    except Exception as e:
        logger.error(f"Terminal data error: {e}")
        return {"categories": {"PERP": [], "SPOT": [], "TRENDING": []}, "prices": {}}


# ============================================================
# TRADINGVIEW UDF DATAFEED (HIP-4)
# ============================================================

@router.get("/udf/config")
async def udf_config():
    """TradingView UDF configuration endpoint."""
    return {
        "supports_search": True,
        "supports_group_request": False,
        "supported_resolutions": ["1", "5", "15", "30", "60", "240", "D", "W"],
        "supports_marks": False,
        "supports_timescale_marks": False,
        "supports_time": True
    }

@router.get("/udf/symbols")
async def udf_symbols(symbol: str = ""):
    """Search symbols from HIP-4 universe."""
    try:
        from core.asset_universe import get_universe
        
        # Ensure universe is loaded
        universe = get_universe()
        universe._ensure_fresh()
        
        categories = universe.get_categorized_assets()
        
        # Combine all assets from all categories
        all_assets = set()
        for cat_name, cat_assets in categories.items():
            if isinstance(cat_assets, list):
                all_assets.update(cat_assets)
        
        # Filter by search query if provided
        if symbol:
            filtered = [a for a in all_assets if symbol.upper() in a.upper()]
        else:
            # Return all assets if no search query
            filtered = list(all_assets)
        
        # Format for TradingView
        symbols = []
        for asset in sorted(filtered)[:100]:  # Limit results
            symbols.append({
                "name": asset,
                "full_name": f"HYPERLIQUID:{asset}",
                "description": f"{asset} Perpetual on Hyperliquid",
                "exchange": "HYPERLIQUID",
                "ticker": asset,
                "type": "crypto",
                "session": "24x7",
                "timezone": "Etc/UTC",
                "minmov": 1,
                "minmove2": 0,
                "pricescale": 100,
                "has_intraday": True,
                "has_no_volume": False,
                "supported_resolutions": ["1", "5", "15", "30", "60", "240", "D", "W"],
                "volume_precision": 2,
                "data_status": "streaming"
            })
        
        logger.info(f"UDF symbols: returned {len(symbols)} assets for query '{symbol}'")
        return symbols
    except Exception as e:
        logger.error(f"UDF symbols error: {e}", exc_info=True)
        return []

@router.get("/udf/history")
async def udf_history(symbol: str, resolution: str, from_time: int, to_time: int):
    """Fetch candle history from HIP-4 for TradingView."""
    try:
        from core.data_fetcher import _fetch_hl_candles
        
        # Map resolution to interval
        resolution_map = {
            "1": "1m",
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "240": "4h",
            "D": "1d",
            "W": "1w"
        }
        interval = resolution_map.get(resolution, "1h")
        
        # Calculate lookback days based on time range
        lookback_days = max(1, (to_time - from_time) // 86400)
        
        # Fetch candles
        candles = _fetch_hl_candles(symbol, interval, lookback_days)
        
        if not candles:
            return {"s": "no_data"}
        
        # Transform to UDF format
        times = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for c in candles:
            times.append(c["t"] // 1000)
            opens.append(float(c["o"]))
            highs.append(float(c["h"]))
            lows.append(float(c["l"]))
            closes.append(float(c["c"]))
            volumes.append(float(c.get("v", 0)))
        
        return {
            "s": "ok",
            "t": times,
            "o": opens,
            "h": highs,
            "l": lows,
            "c": closes,
            "v": volumes
        }
    except Exception as e:
        logger.error(f"UDF history error for {symbol}: {e}")
        return {"s": "error", "errmsg": str(e)}

@router.post("/close")
async def dashboard_close_position(request: Request, user: dict = Depends(require_role("ADMIN", "OPERATOR"))):
    """Close a position completely using unified core logic."""
    try:
        import json as json_module
        raw_body = await request.body()
        try:
            body = json_module.loads(raw_body)
        except json_module.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # 1. SECURITY: Enforce OTP
        _validate_otp_or_raise(user, str(body.get("otp", "")))
        
        # 2. PARSE INPUT
        asset = str(body.get("asset", "")).strip().upper()
        if not asset:
            raise HTTPException(status_code=400, detail="Asset required")
        
        # 3. EXECUTE VIA UNIFIED CORE LOGIC
        executor = app_context.executor

        # Capture live size/side BEFORE closing, purely for ledger logging —
        # close_position()'s own result has no size field (only order_id/avg_price/status).
        _pre_close_size = 0.0
        _pre_close_side = ""
        try:
            _positions = executor.get_open_positions()
            _target = next((p for p in _positions if p.get("coin") == asset.upper()), None)
            if _target:
                _pre_close_size = float(_target.get("size", 0))
                _pre_close_side = _target.get("side", "")
        except Exception as _e:
            logger.error(f"Failed to capture pre-close position size for ledger: {_e}")

        result = executor.close_position(asset)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Close failed"))
        
        # 3.1 LOG TO TRADE LEDGER (Activity panel reads this — without it, closes are invisible there)
        try:
            from core.trade_ledger import record_trade
            exit_price = float(result.get("avg_price", 0) or 0)
            record_trade("close", asset, "MANUAL_DASHBOARD", _pre_close_side,
                          _pre_close_size, exit_price, order_id=result.get("order_id"))
        except Exception as _e:
            logger.error(f"Failed to record close trade in ledger: {_e}")

        # 4. LOG ACTION
        ip = request.client.host if request.client else "unknown"
        log_audit(user["id"], "POSITION_CLOSED", resource=asset, 
                  details=json_module.dumps({"result": str(result)}), ip_address=ip, otp_verified=True)
        
        return {"status": "success", "message": f"Position {asset} closed", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard close failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.get("/meta_learner")
async def dashboard_meta_learner(user: dict = Depends(get_current_user)):
    """Expose MetaLearner weights and strategy status to the dashboard."""
    try:
        from core.meta_learner import get_meta_learner
        meta = get_meta_learner()
        
        return {
            "status": "active",
            "weights": meta.weights,
            "strategies": list(next(iter(meta.weights.values())).keys()) if meta.weights else [],
            "regimes": list(meta.weights.keys())
        }
    except Exception as e:
        logger.error(f"MetaLearner status error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/stream/prices")
async def stream_prices():
    """
    Server-Sent Events endpoint for real-time price updates.
    Proxies Hyperliquid WebSocket 'allMids' channel.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_generator():
        import websockets
        try:
            async with websockets.connect("wss://api.hyperliquid.xyz/ws") as ws:
                # Subscribe to all mids (mid prices for all assets)
                await ws.send(json.dumps({
                    "type": "subscribe",
                    "subscription": {"type": "allMids"}
                }))
                
                async for message in ws:
                    data = json.loads(message)
                    if data.get("channel") == "allMids":
                        yield f"data: {json.dumps(data['data']['mids'])}\n\n"
        except Exception as e:
            logger.error(f"SSE WebSocket error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
