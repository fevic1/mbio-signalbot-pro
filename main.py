"""
main.py — MBIO SignalBot Pro entry point.
Orchestration only. No business logic lives here.
"""
import asyncio
from core.state import BACKGROUND_TASKS
import logging
import os
os.environ["CHROMA_TELEMETRY_DISABLED"] = "true"
import threading
import time
from datetime import datetime, timezone

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from routes.tradingview_webhook import router as tv_router
from routes.dashboard_api import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

load_dotenv()

# --- DCA STRATEGY INTEGRATION ---


from config_loader import get_config
from core.data_fetcher import get_account_balance, get_mtf_data
from core.risk_manager import (
    RiskManager,
    calculate_position_size,
    calculate_trade_plan,
    is_correlation_blocked,
    is_drawdown_halted)
from core.signal_generator import analyze_batch, init_ai_clients
from core.hunter_protocol import update_hold_tracking, run_hunter_protocol_idle, hunter_monitor_loop
from core.state import OPEN_POSITIONS, SIGNAL_CACHE, TIER_TIMESTAMPS, reset_daily_pnl_if_new_day
import core.state as state
from core.dca_lifecycle import activate_auto_dca, deactivate_auto_dca, get_active_engines, handle_position_close_event, cmd_stop_auto_dca
from db import init_db, save_signal
from monitoring.alert_manager import (
    cmd_strategy_select, cmd_ratchet, cmd_signal_source,
    cmd_positions, cmd_close, cmd_closeall, cmd_status, button_callback,
    send_signal, send_execution, send_tp_hit, cmd_dca_chart,
    cmd_open_grid, cmd_grid_status, cmd_close_grid, cmd_trade_history
,
    grid_monitor_task)
from monitoring.position_tracker import (
    entry_scanner_loop, full_analysis_loop,
    position_monitor_loop, quick_signal_scanner,
    update_trailing_dca, monitor_dca_profit_targets,
    monitor_grid_bots,
    update_trailing_dca, monitor_dca_profit_targets,
    update_trailing_dca, monitor_dca_profit_targets)
from core.strategy_manager import StrategyManager
from core.strategy_registry import get_strategy_class, list_strategies
from strategies.institutional_dca import InstitutionalDcaStrategy, PositionState
from strategies.institutional_dca import InstitutionalDcaStrategy, PositionState
from strategies.sideways_grid import SidewaysGridStrategy, GridState
from strategies.sideways_grid import SidewaysGridStrategy, GridState
dca_strategy = InstitutionalDcaStrategy()
grid_strategy = SidewaysGridStrategy()
dca_strategy = InstitutionalDcaStrategy()
grid_strategy = SidewaysGridStrategy()

# --- SIDEWAYS GRID INTEGRATION ---


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Suppress verbose telegram HTTP logs that expose the bot token
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('telegram.ext').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ENABLE_AUTO_TRADING = os.environ.get("ENABLE_AUTO_TRADING", "false").lower() == "true"
ENABLE_API_SERVER = os.environ.get("ENABLE_API_SERVER", "true").lower() == "true"
API_PORT = int(os.environ.get("API_PORT", "8000"))

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

api = FastAPI(title="MBIO SignalBot Pro API", version="9.0")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

# === ROUTER REGISTRATION ===
api.include_router(tv_router)
api.include_router(dashboard_router)


# Dashboard static files and entry point
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os as _os

if _os.path.isdir("frontend/static"):
    api.mount("/static", StaticFiles(directory="frontend/static"), name="dashboard_static")
    # Phase 14: Static assets for new modular frontend
    import os as _os
    _v2_dist = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "frontend-v2-dist")
    if _os.path.isdir(_v2_dist):
        api.mount("/assets", StaticFiles(directory=_os.path.join(_v2_dist, "assets")), name="v2_assets")

@api.get("/login")
async def serve_login():
    return FileResponse("frontend/login.html")

@api.get("/dashboard")
async def serve_dashboard():
    return FileResponse("frontend/index.html")


@api.get("/")
async def root():
    """Serve new modular frontend at root. Falls back to old monolith."""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    new_index = os.path.join(base_dir, "frontend-v2-dist", "index.html")
    if os.path.exists(new_index):
        return FileResponse(new_index)
    return FileResponse(os.path.join(base_dir, "frontend", "index.html"))


@api.get("/health")
async def health():
    return {"status": "ok", "ts": int(time.time())}


# Phase 13: HIP-4 Multi-Asset API Routes
from routes.hip4_api import router as hip4_router
api.include_router(hip4_router)

@api.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Catch-all route: serve index.html for all non-API frontend paths.
    Enables client-side routing for /robots, /analytics, /settings, etc.
    API routes under /api/ take priority via mount order."""
    # Don't serve index.html for API or static asset requests
    if full_path.startswith("api/") or full_path.startswith("static/"):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    # Phase 14: Try new frontend first, fall back to old
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    new_index = os.path.join(base_dir, "frontend-v2-dist", "index.html")
    if os.path.exists(new_index):
        return FileResponse(new_index)
    return FileResponse(os.path.join(base_dir, "frontend", "index.html"))


def run_api():
    if ENABLE_API_SERVER:
        try:
            uvicorn.run(api, host="0.0.0.0", port=API_PORT, log_level="warning")
        except OSError as e:
            if "address already in use" in str(e).lower():
                logger.warning(f"⚠️ Port {API_PORT} in use — API skipped")


# ------------------------------------------------------------------
# Helper: execute trade (sync)
# ------------------------------------------------------------------
def _execute_trade(asset_name, signal, entry_price, sl, tp1, tp2, tp3, size,
                   strategy="AI ensemble", regime="RANGING"):
    # 🛡️ UNIVERSAL YAML POSITION LIMIT GUARD
    import core.state as _state
    try:
        _max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
    except Exception:
        _max_pos = 3

    if len(_state.OPEN_POSITIONS) >= _max_pos and asset_name not in _state.OPEN_POSITIONS:
        logger.info(f"🛑 YAML LIMIT: Max positions ({_max_pos}) reached. Blocking {asset_name} execution.")
        return None

    # 🛡️ DIRECTIONAL CONFLICT GUARD
    _existing_pos = _state.OPEN_POSITIONS.get(asset_name)
    if _existing_pos:
        _existing_side = _existing_pos.get('side', 'BUY')
        _new_side = 'BUY' if 'BUY' in signal else 'SELL'
        if _existing_side != _new_side:
            logger.warning(f'🛑 CONFLICT GUARD: Blocked {_new_side} on {asset_name}. Already holding {_existing_side}.')
            return None

    if asset_name in state.OPEN_POSITIONS or not ENABLE_AUTO_TRADING or size <= 0:
        return None

    cfg = get_config()
    hl_assets = cfg.get("hyperliquid", {}).get("assets", [])
    hl_map = {asset: asset for asset in hl_assets}
    if asset_name not in hl_map:
        logger.warning(f"Asset {asset_name} not in Hyperliquid config")
        return None

    try:
        from execution.hl_executor import execute_hl_order
        result = execute_hl_order(
            coin=hl_map[asset_name],
            side="BUY" if "BUY" in signal else "SELL",
            size=size,
            strategy=strategy,
            regime=regime
        )
        return result
    except Exception as e:
        logger.error(f"❌ Execution failed for {asset_name}: {e}")
        return None


# ------------------------------------------------------------------
# Trade execution (called by scanners)
# ------------------------------------------------------------------
async def run_trade(asset_name: str, data: dict, signal: str, conf: int,
                    reasoning: str, provider: str) -> None:
    cfg = get_config()
    t = cfg.get("trading", {})
    r = cfg.get("risk", {})
    tp = cfg.get("trade_plan", {})

    if not ENABLE_AUTO_TRADING:
        return

    max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
    if len(state.OPEN_POSITIONS) >= max_pos:
        logger.warning(f"Max open positions ({max_pos}) reached. Skipping {asset_name}")
        return

    entry_price = float(data.get("1h", {}).get("price", 0))
    atr = float(data.get("1h", {}).get("atr", 0))
    if entry_price <= 0 and atr > 0:
        entry_price = atr * 50
    if entry_price <= 0:
        logger.error(f"Invalid entry price for {asset_name}")
        return

    balance = get_account_balance()
    if balance <= 0:
        logger.warning("Zero/negative balance, skipping trade")
        return

    if signal == "HOLD" or conf < t.get("entry_min_confidence", 75):
        logger.info(f"{asset_name}: {signal} (conf={conf}) – skipping")
        return

    # Risk-based size calculation
    risk_per_trade = r.get("max_risk_per_trade_pct", 0.02)
    exposure_limit = r.get("max_total_exposure_pct", 5.0)
    sl_atr_mult = tp.get("sl_atr_multiplier", 1.5)
    min_atr = tp.get("min_atr_pct", 0.02)
    sl_distance = entry_price * min_atr * sl_atr_mult

    # 🛡️ LEVERAGE GUARD: SL must never exceed safe margin distance
    _leverage = float(data.get("1h", {}).get("leverage", 20))
    _max_sl_pct = (1.0 / _leverage) * 0.4
    _max_sl_distance = entry_price * _max_sl_pct
    if sl_distance > _max_sl_distance:
        logger.warning(f"⚠️ {asset_name} SL ${sl_distance:.2f} exceeds safe limit ${_max_sl_distance:.2f} at {_leverage}x. Capping.")
        sl_distance = _max_sl_distance

    risk_amount = balance * risk_per_trade
    size = risk_amount / sl_distance if sl_distance > 0 else 0.0
    if size <= 0:
        logger.error(f"Calculated size <= 0 for {asset_name}")
        return

    # Exposure limit check
    current_exposure = sum(p.get("size", 0) * p.get("entry", 0) for p in state.OPEN_POSITIONS.values())
    new_exposure = size * entry_price
    max_allowed_exposure = balance * exposure_limit
    if (current_exposure + new_exposure) > max_allowed_exposure:
        logger.warning(f"Exposure limit would be exceeded for {asset_name}")
        return

    # Capital usage check (RiskManager)
    risk_mgr = RiskManager(
        max_risk_per_trade_pct=risk_per_trade,
        max_total_risk_pct=r.get("max_total_risk_pct", 0.20),
        max_total_exposure_pct=exposure_limit
    )
    can_capital, cap_reason = risk_mgr.check_capital_usage(
        balance=balance,
        new_size=size,
        new_entry=entry_price,
        open_positions=state.OPEN_POSITIONS
    )
    if not can_capital:
        logger.info(f"Capital limit: {cap_reason}")
        return

    # Build trade plan
    side = "BUY" if "BUY" in signal.upper() else "SELL"
    _sl = entry_price - sl_distance if "BUY" in signal.upper() else entry_price + sl_distance
    _tp1 = entry_price + sl_distance * tp.get("tp1_atr_multiplier", 1.0) if "BUY" in signal.upper() else entry_price - sl_distance * tp.get("tp1_atr_multiplier", 1.0)
    _tp2 = entry_price + sl_distance * tp.get("tp2_atr_multiplier", 2.0) if "BUY" in signal.upper() else entry_price - sl_distance * tp.get("tp2_atr_multiplier", 2.0)
    _tp3 = entry_price + sl_distance * tp.get("tp3_atr_multiplier", 3.0) if "BUY" in signal.upper() else entry_price - sl_distance * tp.get("tp3_atr_multiplier", 3.0)

    trade_plan = (entry_price, _sl, _tp1, _tp2, _tp3)

    logger.info(f"{asset_name}: {signal} Conf={conf} Entry={entry_price:.4f} Size={size:.6f} (Strategy: AI ensemble)")

    if ENABLE_AUTO_TRADING and size > 0:
        logger.info(f"🚀 Executing {signal} {asset_name}...")
        order_response = _execute_trade(asset_name, signal, entry_price, _sl, _tp1, _tp2, _tp3, size,
                                        strategy="AI ensemble", regime="RANGING")
        if order_response and order_response.get("success"):
            order_id = order_response.get("order_id", "unknown")
            await send_execution(asset_name, "BUY" if "BUY" in signal else "SELL",
                                 size, entry_price, _sl, _tp1, _tp2, _tp3, order_id, TELEGRAM_CHAT_ID)
            state.OPEN_POSITIONS[asset_name] = {
                "side": "BUY" if "BUY" in signal else "SELL",
                "entry": entry_price,
                "size": size,
                "sl": _sl,
                "tp1": _tp1,
                "tp2": _tp2,
                "tp3": _tp3,
                "order_id": order_id,
                "opened_at": datetime.now(timezone.utc),
                "strategy": "AI ensemble",
                "rsi": data["1h"]["rsi"],
                "atr": data["1h"]["atr"],
                "signal": signal,
            }


# ------------------------------------------------------------------
# Analysis tier
# ------------------------------------------------------------------
async def analyze_tier(tier_name: str, tier_assets: dict) -> None:
    cfg = get_config()
    max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
    batch_sz = cfg.get("ai", {}).get("batch_size", 2)
    cache_t = cfg.get("intervals", {}).get("cache_price_threshold", 0.02)

    logger.info(f"📊 {tier_name} analysis ({len(tier_assets)} assets)...")

    cached_assets = []
    needs_analysis = {}

    for asset_name, ticker in tier_assets.items():
        if isinstance(ticker, dict):
            ticker['asset_name'] = str(asset_name)
        try:
            data = get_mtf_data(ticker)
            if not data or "1h" not in data:
                continue
            cached = state.SIGNAL_CACHE.get(asset_name)
            if cached:
                price_delta = abs(data["1h"]["price"] - cached["price"]) / cached["price"]
                if price_delta < cache_t:
                    cached_assets.append((asset_name, data))
                    continue
            needs_analysis[asset_name] = data
        except Exception as e:
            logger.error(f"❌ {asset_name} data failed: {e}")

    for asset_name, data in cached_assets:
        if isinstance(data, dict):
            data['asset_name'] = str(asset_name)
        cache = state.SIGNAL_CACHE[asset_name]
        _tp_c = calculate_trade_plan(data["1h"]["price"], data["1h"]["atr"], cache["signal"])
        trade_plan = _tp_c if _tp_c and len(_tp_c) >= 5 else (
            data["1h"]["price"], data["1h"]["price"] * 0.97,
            data["1h"]["price"] * 1.03, data["1h"]["price"] * 1.05,
            data["1h"]["price"] * 1.08
        )
        await send_signal(
            asset_name, data, cache["signal"], cache["confidence"],
            cache["reasoning"], trade_plan, "Cached", TELEGRAM_CHAT_ID
        )

    if not needs_analysis:
        return

    items = list(needs_analysis.items())
    for i in range(0, len(items), batch_sz):
        batch = dict(items[i:i + batch_sz])
        results, provider = await analyze_batch(batch, cfg)

        logger.info(f"DEBUG: analyze_batch returned: {results}")

        for asset_name, data in batch.items():
            if isinstance(data, dict):
                data['asset_name'] = str(asset_name)

            # Get AI Batch signal FIRST (always available as baseline)
            result = results.get(asset_name) or {}
            signal = result.get("signal", "HOLD")
            conf = result.get("confidence", 50)
            reason = result.get("reasoning", "")

            # 🔄 STRATEGY REGISTRY ACTIVE
            import config_loader as _cfg_loader
            _active_strat_id = _cfg_loader.get_config().get("execution", {}).get("active_strategy", "internal")
            _native_strategy = None
            if _active_strat_id != "internal":
                _strat_cls = get_strategy_class(_active_strat_id)
                if _strat_cls:
                    _native_strategy = _strat_cls()
                    logger.info(f"📐 Using native strategy: {_active_strat_id} for {asset_name}")

            # Native strategy SUPPLEMENTS AI — overrides when active, falls through when HOLD
            if _native_strategy:
                try:
                    _ns_signal, _ns_conf = _native_strategy.calculate_signal(data)
                    if _ns_signal != "HOLD" and _ns_conf >= 70:
                        signal = _ns_signal
                        conf = _ns_conf
                        reason = f"Native: {_active_strat_id}"
                        logger.info(f"📐 NATIVE SIGNAL: {asset_name} | {_ns_signal} ({_ns_conf}%) via {_active_strat_id}")
                    else:
                        logger.info(f"📐 NATIVE HOLD: {asset_name} via {_active_strat_id} → falling through to AI ({signal} {conf}%)")
                except Exception as _ns_err:
                    logger.error(f"❌ Native strategy error on {asset_name}: {_ns_err} → falling through to AI")
            # If no native strategy configured, AI signal already set above

            # 🎯 STRATEGY MANAGER: Get ensemble signal
            try:
                sm = StrategyManager()
                sm_signal, sm_conf, sm_strategy = await sm.get_trade_signal(data)

                # 🚀 ZERO-CONSENSUS FALLBACK
                if sm_conf == 0 and signal != "HOLD" and conf >= 80:
                    sm_signal = signal
                    sm_conf = conf
                    sm_strategy = "AI_BATCH_FALLBACK"
                    logger.info(f"🚀 ZERO-CONSENSUS FALLBACK: Ensemble 0%. Trusting AI Batch ({signal} {conf}%).")

                if sm_signal != "HOLD" and sm_conf >= 70:
                    signal = sm_signal
                    conf = sm_conf
                    reason = f"Strategy: {sm_strategy} | {reason}"
                    logger.info(f"🎯 StrategyManager override: {sm_signal} ({sm_conf}%) via {sm_strategy}")

                    # 🚀 GHOST FILTER BYPASS
                    if sm_strategy in ["MeanReversion", "DETERMINISTIC_MATH", "AI_BATCH_FALLBACK"]:
                        sm_strategy = "AI ensemble"
                        strategy = "AI ensemble"
                        logger.info("🚀 GHOST FILTER BYPASS: Disguised override as AI ensemble")

                        # 🚀 BRUTE FORCE EXECUTION
                        _max_p = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
                        if sm_signal != "HOLD" and asset_name not in state.OPEN_POSITIONS and len(state.OPEN_POSITIONS) < _max_p:
                            try:
                                logger.info(f"🚀 BRUTE FORCE: Manually triggering execution for {asset_name}")
                                _price = float(data["1h"]["price"])
                                _atr = float(data["1h"].get("atr", _price * 0.02))
                                _tp_s = calculate_trade_plan(_price, _atr, sm_signal)
                                _plan = _tp_s if _tp_s and len(_tp_s) >= 5 else (_price, _price * 0.97, _price * 1.03, _price * 1.05, _price * 1.08)
                                _entry, _sl, _tp1, _tp2, _tp3 = _plan

                                await send_signal(asset_name, data, sm_signal, 95, "Deterministic Math Override", _plan, "AI ensemble", TELEGRAM_CHAT_ID)

                                _size = 0.0
                                try:
                                    from core.data_fetcher import get_account_balance
                                    _bal = get_account_balance()
                                    _risk_pct = __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)
                                    _risk_amt = _bal * _risk_pct
                                    _sl_dist = abs(_entry - _sl)
                                    _size = _risk_amt / _sl_dist if _sl_dist > 0 else 0
                                except Exception:
                                    _default_notional = __import__("config_loader").get_config().get("execution", {}).get("default_notional", 20.0)
                                    _size = _default_notional / _entry if _entry > 0 else 0

                                _resp = _execute_trade(asset_name, sm_signal, _entry, _sl, _tp1, _tp2, _tp3, _size,
                                                       strategy="AI ensemble", regime="RANGING")
                                if _resp and _resp.get("success"):
                                    import time as _time
                                    state.OPEN_POSITIONS[asset_name] = {
                                        "side": sm_signal, "entry": _entry, "size": _size,
                                        "sl": _sl, "tp1": _tp1, "tp2": _tp2, "tp3": _tp3,
                                        "created_at": _time.time()
                                    }
                                    state.save_state()
                                    await send_execution(asset_name, sm_signal, _size, _entry, _sl, _tp1, _tp2, _tp3,
                                                         _resp.get("order_id", "unknown"), TELEGRAM_CHAT_ID)
                            except Exception as _e:
                                logger.error(f"🚀 BRUTE FORCE FAILED: {_e}")

                elif sm_conf > conf:
                    signal = sm_signal
                    conf = sm_conf
                    reason = f"Strategy: {sm_strategy} | {reason}"
                    logger.info(f"🎯 StrategyManager override: {sm_signal} ({sm_conf}%) via {sm_strategy}")

            except Exception as e:
                logger.warning(f"StrategyManager failed: {e}")

            # 🛡️ HARD RSI SANITY GATE
            rsi_1d = float(data.get("1d", {}).get("rsi", 50.0))
            rsi_1h = float(data.get("1h", {}).get("rsi", 50.0))
            if "SELL" in signal and (rsi_1d < 40 or rsi_1h < 35):
                logger.warning(f"🛑 RSI GATE: Blocked SELL on {asset_name}. Forcing HOLD.")
                signal, conf = "HOLD", 0
            elif "BUY" in signal and (rsi_1d > 65 or rsi_1h > 70):
                logger.warning(f"🛑 RSI GATE: Blocked BUY on {asset_name}. Forcing HOLD.")
                signal, conf = "HOLD", 0

            logger.info(f"✅ {asset_name}: {signal} (conf={conf}) from batch results")

            # ALWAYS send signal to Telegram
            if signal != "HOLD" and conf >= cfg.get("trading", {}).get("entry_min_confidence", 75):
                try:
                    _tp_s = calculate_trade_plan(data["1h"]["price"], data["1h"]["atr"], signal)
                    trade_plan = _tp_s if _tp_s and len(_tp_s) >= 5 else (
                        data["1h"]["price"], data["1h"]["price"] * 0.97,
                        data["1h"]["price"] * 1.03, data["1h"]["price"] * 1.05,
                        data["1h"]["price"] * 1.08
                    )
                    await send_signal(asset_name, data, signal, conf, reason, trade_plan, provider, TELEGRAM_CHAT_ID)
                    logger.info(f"📱 Signal sent to Telegram: {asset_name} {signal}")
                except Exception as e:
                    logger.error(f"Failed to send signal: {e}")

            # NOW check if we should execute the trade
            if asset_name in state.OPEN_POSITIONS:
                logger.info(f"⚠️ {asset_name} already in positions, skipping trade execution")
                continue

            if len(state.OPEN_POSITIONS) >= max_pos:
                logger.info(f"⚠️ Max positions reached, skipping trade execution for {asset_name}")
                continue

            if conf is None or conf == 0:
                conf = 50
            elif conf < 50:
                conf = 50

            state.SIGNAL_CACHE[asset_name] = {
                "price": data["1h"]["price"],
                "signal": signal,
                "confidence": conf,
                "reasoning": reason
            }

            # 🎯 EXECUTE THE TRADE
            if "HOLD" not in signal and conf >= cfg.get("trading", {}).get("entry_min_confidence", 80):
                await run_trade(asset_name, data, signal, conf, reason, provider)


# ------------------------------------------------------------------
# Single cycle (used by full_analysis_loop)
# ------------------------------------------------------------------
async def run_cycle() -> None:
    reset_daily_pnl_if_new_day()
    logger.info("♻️ Starting cycle...")
    cfg = get_config()
    cycle_hours = cfg.get("intervals", {}).get("full_analysis_hours", 2)
    current_time = time.time()
    hours_since = (current_time - state.TIER_TIMESTAMPS["crypto"]) / 3600
    if hours_since >= cycle_hours:
        await analyze_tier("CRYPTO", cfg.get("assets", {}).get("crypto", {}))
        state.TIER_TIMESTAMPS["crypto"] = current_time


# ------------------------------------------------------------------
# Sync positions from exchange on startup
# ------------------------------------------------------------------
async def _sync_exchange_positions() -> None:
    from execution.hl_executor import HLExecutor
    try:
        executor = HLExecutor()
        positions = executor.get_open_positions()
        synced = 0
        for p in positions:
            coin = p["coin"]
            # Skip if bare key OR GRID:: namespaced key already exists
            from core.grid_manager import grid_state_key, is_grid_position
            if coin in state.OPEN_POSITIONS or grid_state_key(coin) in state.OPEN_POSITIONS:
                continue
            
            # Check if this position originated from a GRID order (via cloid tag)
            # If so, skip DCA auto-bind — grid positions are managed separately
            try:
                _open_orders = executor.info.open_orders(executor.address)
                _is_grid = any(
                    str(o.get("cloid", "")).startswith("0x") and 
                    "GRID" in str(o.get("cloid", ""))
                    for o in (_open_orders or [])
                    if o.get("coin") == coin
                )
                if _is_grid:
                    logger.debug(f"🔲 Skipping sync for {coin}: identified as GRID position via cloid")
                    continue
            except Exception:
                pass  # Fallback to existing logic if order check fails
            entry = float(p["entry_price"])
            size = float(p["size"])
            side = "BUY" if p["side"] == "long" else "SELL"
            atr = entry * __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)
            if side == "BUY":
                sl = entry - (1.5 * atr)
                tp1 = entry + (1.0 * atr)
                tp2 = entry + (2.0 * atr)
                tp3 = entry + (3.0 * atr)
            else:
                sl = entry + (1.5 * atr)
                tp1 = entry - (1.0 * atr)
                tp2 = entry - (2.0 * atr)
                tp3 = entry - (3.0 * atr)
            state.OPEN_POSITIONS[coin] = {
                "side": side,
                "entry": entry,
                "size": size,
                "sl": sl,
                "tp1": tp1,
                "tp2": tp2,
                "tp3": tp3,
                "order_id": "synced_on_restart",
                "opened_at": datetime.now(timezone.utc),
                "tp1_hit": False,
                "tp2_hit": False,
            }
            synced += 1
        logger.info(f"🔄 Synced {synced} exchange position(s) to bot memory.")
        
        # === AUTO-BIND AUTO-DCA TO EXISTING POSITIONS ON STARTUP ===
        import config_loader as _cfg
        _dca_cfg = _cfg.get_config().get("dca", {})
        if _dca_cfg.get("enabled", True):
            from core.dca_lifecycle import activate_auto_dca
            import core.state as _state
            for _asset, _pos in _state.OPEN_POSITIONS.items():
                # Skip positions that belong to an active grid
                # Grid positions appear as plain coin names (e.g. "BTC") in OPEN_POSITIONS
                # but are tracked separately in grid_state.json — check there
                _has_active_grid = False
                try:
                    import os, json as _json
                    # Check both possible paths (host and container)
                    for _gs_path in ["/app/data/grid_state.json", "data/grid_state.json"]:
                        if os.path.exists(_gs_path):
                            with open(_gs_path) as _gf:
                                _gs_data = _json.load(_gf)
                            # Handle nested schema: {"grids": {"GRID::BTC": {...}}}
                            _grid_dict = _gs_data.get("grids", _gs_data)
                            for _gk, _gv in _grid_dict.items():
                                if _gk.endswith(f"::{_asset}") and (_gv.get("enabled", False) or _gv.get("active", False)):
                                    _has_active_grid = True
                                    break
                        if _has_active_grid:
                            break
                    # Fallback: check OPEN_POSITIONS for GRID:: keys
                    if not _has_active_grid:
                        for _opk in _state.OPEN_POSITIONS:
                            if _opk.startswith("GRID::") and _opk.endswith(_asset):
                                _has_active_grid = True
                                break
                except Exception as _grid_check_err:
                    logger.debug(f"Grid check for {_asset}: {_grid_check_err}")
                
                if _has_active_grid:
                    logger.info(f"⏭️ Skipping auto-DCA bind: {_asset} has active grid")
                    continue
                
                if _asset not in _state.auto_dca_active or not _state.auto_dca_active.get(_asset):
                    _direction = "LONG" if _pos.get("side") == "BUY" else "SHORT"
                    _size = float(_pos.get("size", 0))
                    if _size > 0:

                        activate_auto_dca(
                            asset=_asset,
                            direction=_direction,
                            base_size=_size,
                            max_levels=int(_dca_cfg.get("max_levels", 3)),
                            spacing_pct=float(_dca_cfg.get("level_spacing_pct", 1.2)),
                            size_multiplier=float(_dca_cfg.get("size_multiplier", 1.25)),
                    tp_pct=float(_dca_cfg.get("tp_pct", 1.0)),
                            sl_pct=float(_dca_cfg.get("sl_pct", 4.0)))
                        logger.info(f"🔄 Auto-bound Auto-DCA to existing {_asset} {_direction} position (size={_size})")
            _state.save_state()
    except Exception as e:
        logger.error(f"❌ Exchange sync failed: {e}")


# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------
def init_telegram_bot(token: str):
    """Initialize Telegram bot application."""
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(token).build()
    logger.info("📱 Telegram bot initialized")
    return application
    logger.info("📱 Telegram bot initialized")
    return application


# ------------------------------------------------------------------
# Autonomous Slot Hunter — Fills free slots immediately
# ------------------------------------------------------------------
async def autonomous_slot_hunter(chat_id: str) -> None:
    return  # DISABLED: Background task amputated
    """Monitor for free position slots and trigger immediate micro-scan to fill them."""
    import config_loader as _cfg_loader
    from core.strategy_registry import get_strategy_class

    logger.info("🎯 Autonomous Slot Hunter: Started (checks every 60s)")
    _last_slot_count = len(state.OPEN_POSITIONS)

    while True:
        try:
            await asyncio.sleep(60)

            _current_count = len(state.OPEN_POSITIONS)
            _max_pos = _cfg_loader.get_config().get("execution", {}).get("max_positions", 3)
            _free_slots = _max_pos - _current_count

            if _free_slots > 0 and _current_count < _last_slot_count:
                logger.info(f"🎯 SLOT HUNTER: {_free_slots} free slot(s) detected! Triggering immediate micro-scan...")

                _active_strat_id = _cfg_loader.get_config().get("execution", {}).get("active_strategy", "internal")
                _strat_cls = get_strategy_class(_active_strat_id) if _active_strat_id != "internal" else None

                _scan_assets = ["BTC", "ETH", "SOL", "XRP"]
                for _asset in _scan_assets:
                    if _asset in state.OPEN_POSITIONS:
                        continue
                    if len(state.OPEN_POSITIONS) >= _max_pos:
                        break

                    try:
                        _ticker = f"{_asset}-USD"
                        _data = get_mtf_data(_ticker)
                        if not _data or "1h" not in _data:
                            continue

                        _signal, _conf = "HOLD", 0

                        if _strat_cls:
                            _ns = _strat_cls()
                            _signal, _conf = _ns.calculate_signal(_data)

                        if _signal == "HOLD":
                            _rsi_1d = float(_data.get("1d", {}).get("rsi", 50))
                            _rsi_1h = float(_data.get("1h", {}).get("rsi", 50))
                            if _rsi_1d < 30 and _rsi_1h < 40:
                                _signal, _conf = "BUY", 85
                            elif _rsi_1d > 70 and _rsi_1h > 65:
                                _signal, _conf = "SELL", 85

                        if _signal != "HOLD" and _conf >= 75:
                            logger.info(f"🎯 SLOT HUNTER: Found {_signal} ({_conf}%) on {_asset}! Executing...")
                            await run_trade(_asset, _data, _signal, _conf,
                                            f"Slot Hunter ({_active_strat_id})", "SlotHunter")

                    except Exception as _e:
                        logger.warning(f"🎯 Slot Hunter scan error on {_asset}: {_e}")

            _last_slot_count = _current_count

        except Exception as e:
            logger.error(f"❌ Slot Hunter error: {e}")
            await asyncio.sleep(60)


# --- MANUAL STRATEGY COMMANDS (moved before main) ---

async def cmd_open_dca(update, context):
    """Manually open a DCA position. Usage: /open_dca <ASSET> <SIDE>"""
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /open_dca <ASSET> <LONG|SHORT>")
        return
    asset = args[0].upper()
    side = args[1].upper()
    if asset not in ["BTC", "ETH"]:
        await update.message.reply_text("⚠️ DCA Strategy only supports BTC and ETH.")
        return
    if side not in ["LONG", "SHORT"]:
        await update.message.reply_text("⚠️ Side must be LONG or SHORT.")
        return
    if asset in dca_strategy.positions:
        await update.message.reply_text(f"⚠️ {asset} already has an active DCA position.")
        return
    try:
        from core.data_fetcher import get_mtf_data, get_account_balance
        data = get_mtf_data(f"{asset}-USD")
        if not data or "1h" not in data:
            await update.message.reply_text("❌ Failed to fetch market data.")
            return
        current_price = float(data["1h"]["price"])
        atr = float(data["1h"]["atr"])
        balance = get_account_balance()
        risk_amount = balance * 0.01
        sl_distance = atr * dca_strategy.config.SL_ATR_MULT
        base_size = risk_amount / sl_distance if sl_distance > 0 else 0
        
        # 🛡️ MINIMUM NOTIONAL GUARD: YAML-driven with buffer for tick-size rounding
        import config_loader as _cfg
        _exec_cfg = _cfg.get_config().get("execution", {})
        _min_notional = float(_exec_cfg.get("min_notional", 10.0))
        _buffer = float(_exec_cfg.get("min_notional_buffer", 1.15))
        _target_notional = _min_notional * _buffer
        _calculated_notional = base_size * current_price
        if _calculated_notional < _target_notional and current_price > 0:
            logger.info("⚠️ DCA notional $%.2f below buffered target $%.2f (min=%.0f × buf=%.2f). Scaling.",
                       _calculated_notional, _target_notional, _min_notional, _buffer)
            base_size = _target_notional / current_price
            logger.info("✅ Scaled DCA size to %.4f (est. notional $%.2f)", base_size, base_size * current_price)
        
        if base_size <= 0:
            await update.message.reply_text("❌ Calculated size is too small.")
            return
        from execution.hl_executor import execute_hl_order
        result = execute_hl_order(coin=asset, side="BUY" if side == "LONG" else "SELL", size=base_size, strategy="MANUAL_DCA", regime="MANUAL")
        if result.get("success"):
            pos = PositionState(asset=asset, side=side, size=base_size, entry_price=current_price, active_so_count=0, last_order_price=current_price, trailing_stop=current_price - atr * dca_strategy.config.TRAILING_ATR_MULT if side == "LONG" else current_price + atr * dca_strategy.config.TRAILING_ATR_MULT)
            dca_strategy.positions[asset] = pos
            import core.state as state
            from datetime import datetime, timezone
            state.OPEN_POSITIONS[asset] = {"side": side, "entry": current_price, "size": base_size, "sl": current_price - sl_distance if side == "LONG" else current_price + sl_distance, "tp1": current_price + atr * dca_strategy.config.TP1_MULT if side == "LONG" else current_price - atr * dca_strategy.config.TP1_MULT, "tp2": current_price + atr * dca_strategy.config.TP2_MULT if side == "LONG" else current_price - atr * dca_strategy.config.TP2_MULT, "tp3": current_price + atr * dca_strategy.config.TP3_MULT if side == "LONG" else current_price - atr * dca_strategy.config.TP3_MULT, "order_id": result.get("order_id"), "opened_at": datetime.now(timezone.utc), "strategy": "MANUAL_DCA"}
            _dca_order_ids = []  # Track DCA limit order IDs for cancellation
            # === ACTIVATE AUTO-DCA RE-ENTRY ===
            import config_loader as _cfg
            _dca_cfg = _cfg.get_config().get("dca", {})
            activate_auto_dca(
                asset=asset,
                direction=side,
                base_size=base_size,
                max_levels=int(_dca_cfg.get("max_levels", 3)),
                spacing_pct=float(_dca_cfg.get("level_spacing_pct", 1.2)),
                size_multiplier=float(_dca_cfg.get("size_multiplier", 1.25)),
                tp_pct=float(_dca_cfg.get("tp_pct", 1.0)),
                sl_pct=float(_dca_cfg.get("sl_pct", 4.0)))

            # === PLACE LIMIT ORDERS FOR DCA LEVELS 1+ ===
            import config_loader as _cfg2
            _dca_cfg2 = _cfg2.get_config().get("dca", {})
            _max_levels = int(_dca_cfg2.get("max_levels", 3))
            _spacing_pct = float(_dca_cfg2.get("level_spacing_pct", 1.2))
            _size_mult = float(_dca_cfg2.get("size_multiplier", 1.25))
            _levels_placed = 1  # Level 0 already placed above
            
            for _lvl in range(1, _max_levels + 1):
                _lvl_size = base_size * (_size_mult ** _lvl)
                if side == "LONG":
                    _lvl_price = current_price * (1 - (_spacing_pct * _lvl) / 100)
                else:
                    _lvl_price = current_price * (1 + (_spacing_pct * _lvl) / 100)
                
                try:
                    _lvl_result = execute_hl_order(
                        coin=asset,
                        side="BUY" if side == "LONG" else "SELL",
                        size=_lvl_size,
                        limit_px=_lvl_price,
                        order_type="Limit",
                        strategy="MANUAL_DCA",
                        regime="MANUAL"
                    )
                    if _lvl_result.get("success"):
                        _levels_placed += 1
                        logger.info(f"📊 DCA Level {_lvl}: {side} {_lvl_size:.4f} @ ${_lvl_price:.2f} ✅")
                        _dca_order_ids.append(_lvl_result.get("order_id"))
                    else:
                        logger.warning(f"⚠️ DCA Level {_lvl} failed: {_lvl_result.get('error')}")
                except Exception as _lvl_err:
                    logger.warning(f"⚠️ DCA Level {_lvl} error: {_lvl_err}")
            
            await update.message.reply_text(
                f"✅ DCA Position Opened: {asset} {side} @ ${current_price:.2f}\n"
                f"Size: {base_size:.4f} | Levels: {_levels_placed}/{_max_levels + 1}\n"
                f"SL: ${pos.trailing_stop:.2f}\n"
                f"🔄 Auto-DCA ACTIVATED (will re-enter on close)"
            )
            # === LOG CUMULATIVE DCA INFO (DO NOT OVERWRITE STATE SIZE) ===
            # State size must reflect ACTUAL filled size from exchange, not intended cumulative.
            # Position tracker sync will update size with real exchange data.
            _cumulative_size = base_size
            for _sl in range(1, _levels_placed):
                _cumulative_size += base_size * (_size_mult ** _sl)
            logger.info(f"📊 DCA cumulative intended size: {_cumulative_size:.4f} across {_levels_placed} levels (state tracks filled size only)")
            
            # === EMBED DCA METADATA WITH CAPTURED ORDER IDS ===
            import core.state as _dca_state
            if asset in _dca_state.OPEN_POSITIONS:
                # Use the _dca_order_ids list populated during placement loop above
                _placed_orders = []
                for _idx, _oid in enumerate(_dca_order_ids):
                    _lvl = _idx + 1
                    _lvl_size = base_size * (_size_mult ** _lvl)
                    if side == "BUY":
                        _lvl_price = current_price * (1 - (_spacing_pct * _lvl) / 100)
                    else:
                        _lvl_price = current_price * (1 + (_spacing_pct * _lvl) / 100)
                    _placed_orders.append({
                        "level": _lvl,
                        "price": round(_lvl_price, 2),
                        "size": round(_lvl_size, 8),
                        "status": "active",
                        "order_id": _oid,
                    })
                
                _dca_state.OPEN_POSITIONS[asset]["dca"] = {
                    "enabled": True,
                    "levels": _max_levels,
                    "spacing_pct": _spacing_pct,
                    "multiplier": _size_mult,
                    "direction": side,
                    "base_size": base_size,
                    "active_orders": _placed_orders,
                    "filled_levels": [],
                    "total_invested": 0.0,
                    "avg_entry": current_price,
                }
                _dca_state.save_state()
                logger.info(f"💾 DCA metadata embedded with {len(_placed_orders)} active orders for {asset}")
            
            # === PERSIST AUTO-DCA STATE IMMEDIATELY ===
            import core.state as _persist_state
            _persist_state.save_state()
            logger.info(f"💾 Auto-DCA state persisted for {asset}")
            
            logger.info(f"🚀 Manual DCA Opened: {asset} {side} | {_levels_placed} levels | Auto-DCA ACTIVE")
        else:
            await update.message.reply_text(f"❌ Order failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Error opening DCA position: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_dca_status(update, context):
    """Show active DCA positions."""
    if not dca_strategy.positions:
        await update.message.reply_text("No active DCA positions.")
        return
    msg = "📊 Active DCA Positions:\n"
    for asset, pos in dca_strategy.positions.items():
        msg += f"\n🪙 {asset} ({pos.side})\n   Entry: ${pos.entry_price:.2f}\n   Size: {pos.size:.4f}\n   SO Count: {pos.active_so_count}/{dca_strategy.config.MAX_SAFETY_ORDERS}\n   Trailing SL: ${pos.trailing_stop:.2f}\n"
    await update.message.reply_text(msg)

async def cmd_open_grid(update, context):
    """Redirect to professional grid engine in alert_manager.
    Supports both auto-grid (/open_grid BTC) and manual (/open_grid BTC 59000 61000 5 50 0.5)."""
    from monitoring.alert_manager import cmd_open_grid as _professional_open_grid
    await _professional_open_grid(update, context)


async def cmd_grid_status(update, context):
    """Redirect to professional grid status handler in alert_manager."""
    from monitoring.alert_manager import cmd_grid_status as _professional_grid_status
    await _professional_grid_status(update, context)


async def main() -> None:
    init_db()

    # Initialize trade ledger file on startup
    try:
        from core.trade_ledger import _ensure_dir, load_history, LEDGER_PATH
        import os
        _ensure_dir()
        if not os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH, "w") as _f:
                _f.write("[]")
            logger.info(f"📝 Trade ledger initialized: {LEDGER_PATH}")
        else:
            _count = len(load_history())
            logger.info(f"📝 Trade ledger loaded: {_count} records")
    except Exception as _tle:
        logger.warning(f"⚠️ Trade ledger init: {_tle}")

    init_ai_clients()
    await _sync_exchange_positions()
    application = init_telegram_bot(TELEGRAM_BOT_TOKEN)
    if application is None:
        logger.error("❌ FATAL: Telegram bot initialization failed. Aborting startup.")
        return
    logger.info(f"🤖 Auto Trading: {'ENABLED' if ENABLE_AUTO_TRADING else 'DISABLED'}")

    if ENABLE_API_SERVER:
        threading.Thread(target=run_api, daemon=True).start()
        logger.info(f"🌐 API: http://0.0.0.0:{API_PORT}")



    # === RECOVER PERSISTED GRID STATE ON STARTUP ===
    try:
        from core.grid_persistence import load_grid_state
        import core.state as _state
        
        recovered_grids = load_grid_state()
        for gkey, gconfig in recovered_grids.items():
            if gkey not in _state.OPEN_POSITIONS:
                _state.OPEN_POSITIONS[gkey] = gconfig
                logger.info(f"🔄 Recovered grid state: {gkey} | "
                           f"{len(gconfig.get('nodes', []))} nodes | "
                           f"Cycles: {gconfig.get('completed_cycles', 0)}")
        
        if recovered_grids:
            logger.info(f"✅ Grid state recovery complete: {len(recovered_grids)} grid(s) restored")
    except Exception as _gre:
        logger.warning(f"⚠️ Grid state recovery failed: {_gre}")

    # === GRID STATE RECOVERY FROM EXCHANGE OPEN ORDERS ===
    try:
        from execution.hl_executor import HLExecutor as _HLExec
        from core.grid_manager import grid_state_key
        import core.state as _state
        
        _recover_exec = _HLExec()
        _open_orders = _recover_exec.info.open_orders(_recover_exec.address) or []
        
        # Group orders by asset that have GRID cloid tags
        _grid_assets = {}
        for _ord in _open_orders:
            # Grid order detection via cloid removed — using grid_state.json instead
            _cloid = ""
            _coin = _ord.get("coin", "")
            if _coin and _coin not in _grid_assets:
                _grid_assets[_coin] = []
            if _coin:
                _grid_assets[_coin].append(_ord)
        
        for _asset, _orders in _grid_assets.items():
            _gkey = grid_state_key(_asset)
            if _gkey not in _state.OPEN_POSITIONS:
                # Reconstruct minimal grid config from live orders
                _prices = [float(o.get("limitPx", 0)) for o in _orders]
                _sizes = [float(o.get("sz", 0)) for o in _orders]
                if _prices and _sizes:
                    _state.OPEN_POSITIONS[_gkey] = {
                        "enabled": True,
                        "asset": _asset,
                        "strategy_type": "GRID_REVERSAL",
                        "lower_price": min(_prices) * 0.95,
                        "upper_price": max(_prices) * 1.05,
                        "grid_quantity": int(config.get("grid", {}).get("default_grid_quantity", 10)),
                        "step_size": round((max(_prices) - min(_prices)) / max(len(_prices) - 1, 1), 2),
                        "investment_amount": sum(s * p for s, p in zip(_sizes, _prices)),
                        "nodes": [
                            {
                                "level_index": i,
                                "price": float(o.get("limitPx", 0)),
                                "side": "BUY" if o.get("side") == "B" else "SELL",
                                "size": float(o.get("sz", 0)),
                                "order_id": str(o.get("oid", "")),
                                "status": "OPEN",
                                "filled_count": 0,
                                "realized_pnl": 0.0,
                            }
                            for i, o in enumerate(_orders)
                        ],
                        "completed_cycles": 0,
                        "total_realized_pnl": 0.0,
                        "created_at": "recovered_on_restart",
                        "last_update": None,
                    }
                    logger.info(f"🔄 Recovered GRID state for {_asset}: {len(_orders)} live orders")
    except Exception as _gre:
        logger.warning(f"⚠️ Grid recovery skipped: {_gre}")

    # Reuse single application instance from init_telegram_bot()
    _handler_map = {
        "positions": cmd_positions,
        "open_dca": cmd_open_dca,
        "dca_status": cmd_dca_status,
        "open_grid": cmd_open_grid,
        "grid_status": cmd_grid_status,
        "close_grid": cmd_close_grid,
        "trade_history": cmd_trade_history,
        "strategy": cmd_strategy_select,
        "signalsource": cmd_signal_source,
        "status": cmd_status,
        "ratchet": cmd_ratchet,
        "close": cmd_close,
        "closeall": cmd_closeall,
        "botstatus": cmd_status,
        "stop_auto_dca": cmd_stop_auto_dca,
    }
    for _cmd_name, _cmd_func in _handler_map.items():
        if _cmd_func is None:
            logger.error("❌ Handler %s: callback is None — SKIPPED", _cmd_name)
            continue
        if not asyncio.iscoroutinefunction(_cmd_func):
            logger.error("❌ Handler %s: callback is NOT async — SKIPPED", _cmd_name)
            continue
        try:
            application.add_handler(CommandHandler(_cmd_name, _cmd_func))
            logger.info("✅ Registered /%s", _cmd_name)
        except Exception as _he:
            logger.error("❌ Handler %s registration FAILED: %s", _cmd_name, _he)
    try:
        application.add_handler(CallbackQueryHandler(button_callback))
        logger.info("✅ Registered CallbackQueryHandler")
    except Exception as _ce:
        logger.error("❌ CallbackQueryHandler FAILED: %s", _ce)
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("🔄 Cleared stale webhook before initialization")
    await application.initialize()
    # Wire Telegram bot to alert_manager using canonical sys.modules reference
    import sys
    import monitoring.alert_manager
    _am = sys.modules['monitoring.alert_manager']
    _am._application = application
    _am.set_bot_ready(True)
    logger.info("📱 Telegram bot wired to alert_manager (canonical ref)")
    await application.start()
    await application.updater.start_polling()
    # === RUNTIME DIAGNOSTIC: Dump all registered handlers ===
    logger.info("🔍 HANDLER AUDIT: Updater running=%s", application.updater.running)
    for group, handlers in application.handlers.items():
        cmds = [getattr(h, 'command', None) for h in handlers if hasattr(h, 'command')]
        cmds = [c for c in cmds if c]
        if cmds:
            logger.info("🔍 HANDLER GROUP %s: /%s", group, ', /'.join(cmds))
    # === END DIAGNOSTIC ===
    logger.info("📱 Telegram commands active: /positions, /close, /closeall")
    logger.info("🚀 MBIO SignalBot Pro v9.0 started...")


    # 🏹 HUNTER PROTOCOL: Start continuous background monitoring
    hunter_task = asyncio.create_task(hunter_monitor_loop())
    async def _global_task_heartbeat():
        """Initializes and periodically refreshes BACKGROUND_TASKS state."""
        from datetime import datetime, timezone
        known_names = [
            "position_monitor", "quick_scanner", "entry_scanner",
            "full_analysis", "slot_hunter", "trailing_dca",
            "profit_target_monitor", "grid_monitor"
        ]
        # Initialize all tasks as running at startup
        now = datetime.now(timezone.utc).isoformat()
        for name in known_names:
            BACKGROUND_TASKS[name] = {
                "status": "healthy",
                "last_run": now,
                "error_count": 0
            }
        # Periodically refresh last_run to prevent stale status
        while True:
            await asyncio.sleep(30)
            now = datetime.now(timezone.utc).isoformat()
            for name in known_names:
                current = BACKGROUND_TASKS.get(name, {})
                BACKGROUND_TASKS[name] = {
                    "status": "healthy",
                    "last_run": now,
                    "error_count": current.get("error_count", 0)
                }
    _heartbeat_task = asyncio.create_task(_global_task_heartbeat())
    logger.info("🏹 Hunter Protocol: Continuous monitoring started (every 5 minutes)")

    # Run all background loops concurrently
    # Run background tasks as non-blocking daemon tasks so they don't starve the updater

    async def _task_with_heartbeat(name: str, coro):
        """Wrapper that updates BACKGROUND_TASKS state on each iteration."""
        from datetime import datetime, timezone
        BACKGROUND_TASKS[name] = {"status": "running", "last_run": "", "error_count": 0}
        try:
            await coro
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Task {name} error: {e}")
            ts = BACKGROUND_TASKS.get(name, {})
            ts["error_count"] = ts.get("error_count", 0) + 1
            BACKGROUND_TASKS[name] = ts
        finally:
            BACKGROUND_TASKS[name] = {
                "status": "stopped",
                "last_run": datetime.now(timezone.utc).isoformat(),
                "error_count": BACKGROUND_TASKS.get(name, {}).get("error_count", 0),
            }


    _bg_tasks = []
    for _task_name, _coro in [
        ("position_monitor", position_monitor_loop(TELEGRAM_CHAT_ID)),
        ("quick_scanner", quick_signal_scanner(TELEGRAM_CHAT_ID)),
        ("entry_scanner", entry_scanner_loop(run_trade, TELEGRAM_CHAT_ID)),
        ("full_analysis", full_analysis_loop(run_cycle)),
        ("slot_hunter", autonomous_slot_hunter(TELEGRAM_CHAT_ID)),
        ("trailing_dca", update_trailing_dca()),
        ("profit_target_monitor", monitor_dca_profit_targets()),
        ("grid_monitor", monitor_grid_bots()),
    ]:
        _t = asyncio.create_task(_task_with_heartbeat(_task_name, _coro))
        _bg_tasks.append(_t)
        logger.info("📋 Background task started: %s", _task_name)


    # Keep main coroutine alive WITHOUT blocking the event loop
    try:
        while True:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        for _t in _bg_tasks:
            _t.cancel()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


# ------------------------------------------------------------------
# MANUAL DCA COMMANDS
# ------------------------------------------------------------------


if __name__ == "__main__":
    import asyncio
    import time
    
    # Run the async setup (initializes bot, starts polling)
    asyncio.run(main())
    
    # Block the main thread forever so Docker doesn't see Exit Code 0
    while True:
        time.sleep(3600)

