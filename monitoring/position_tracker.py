import asyncio
import logging
from datetime import datetime, timezone, timedelta

import core.state as state
from config_loader import get_config
from core.data_fetcher import get_all_live_prices, get_current_price
from core.risk_manager import is_drawdown_halted
from monitoring.alert_manager import send_closure, send_tp_hit
from execution.hl_executor import execute_hl_order

logger = logging.getLogger(__name__)

async def check_and_close_positions(chat_id: str) -> None:
    if not state.OPEN_POSITIONS:
        return
    logger.info(f"🔍 Checking {len(state.OPEN_POSITIONS)} open positions...")

    # 🛡️ ARCHITECTURAL FIX: Institutional Position Telemetry
    from datetime import datetime
    try:
        from core.data_fetcher import get_current_price
    except ImportError:
        pass
    _now_ts = datetime.now().timestamp()
    for _asset, _pos in list(state.OPEN_POSITIONS.items()):
        _entry = float(_pos.get("entry", 0))
        _size = float(_pos.get("size", 0))
        _side = _pos.get("side", "BUY")
        _sl = float(_pos.get("sl", 0))
        _created = _pos.get("created_at", _now_ts)
        _age_hrs = (_now_ts - _created) / 3600
        try:
            _current = get_current_price(f"{_asset}-USD")
            _pnl_pct = ((_current - _entry) / _entry * 100) if _side == "BUY" else ((_entry - _current) / _entry * 100)
            _r_mult = _pnl_pct / 2.0  # Approximate R-multiple based on 2% risk unit
            
            # 🛡️ ARCHITECTURAL FIX: Real Hunter Protocol (Capital Efficiency Check)
            if _age_hrs > 24.0 and abs(_pnl_pct) < 1.0:
                logger.warning(f"🏹 HUNTER: {_asset} is STAGNANT (Age: {_age_hrs:.1f}h, PnL: {_pnl_pct:+.2f}%). Consider manual closure to free margin.")
            elif _pnl_pct < -5.0:
                logger.warning(f"🏹 HUNTER: {_asset} is BLEEDING (PnL: {_pnl_pct:+.2f}%). Approaching critical drawdown.")

            logger.info(f"📊 TELEMETRY: {_asset} {_side} | Entry: ${_entry:.4f} | Current: ${_current:.4f} | PnL: {_pnl_pct:+.2f}% | R: {_r_mult:+.2f} | SL: ${_sl:.4f} | Age: {_age_hrs:.1f}h")
        except Exception:
            
            # 🛡️ ARCHITECTURAL FIX: Real Hunter Protocol (Capital Efficiency Check)
            if _age_hrs > 24.0 and abs(_pnl_pct) < 1.0:
                logger.warning(f"🏹 HUNTER: {_asset} is STAGNANT (Age: {_age_hrs:.1f}h, PnL: {_pnl_pct:+.2f}%). Consider manual closure to free margin.")
            elif _pnl_pct < -5.0:
                logger.warning(f"🏹 HUNTER: {_asset} is BLEEDING (PnL: {_pnl_pct:+.2f}%). Approaching critical drawdown.")

            logger.info(f"📊 TELEMETRY: {_asset} {_side} | Entry: ${_entry:.4f} | SL: ${_sl:.4f} | Age: {_age_hrs:.1f}h (Price fetch failed)")
    cfg = get_config()
    hl_raw = cfg.get("hyperliquid", {}).get("assets", {})
    hl_assets = hl_raw if isinstance(hl_raw, dict) else {a: a for a in hl_raw}
    live_prices = get_all_live_prices([hl_assets.get(k, k) for k in state.OPEN_POSITIONS.keys()])
    assets_to_remove = []
    for asset, pos in list(state.OPEN_POSITIONS.items()):
        try:
            current_price = live_prices.get(hl_assets.get(asset, asset), get_current_price(f"{asset}-USD"))
            if current_price == 0:
                continue
            should_close = False

            # ============================================
            # POSITION AGE TRACKING
            # ============================================
            cfg_age = get_config().get("position_age", {})
            if cfg_age.get("enabled", False):
                opened_at = pos.get("opened_at")
                if opened_at:
                    # Parse datetime if string
                    if isinstance(opened_at, str):
                        try:
                            opened_at = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
                        except:
                            opened_at = None
                    
                    if opened_at:
                        age_hours = (datetime.now(timezone.utc) - opened_at).total_seconds() / 3600
                        max_age = cfg_age.get("max_age_hours", 72)
                        warning_age = cfg_age.get("warning_age_hours", 48)
                        exclude = cfg_age.get("exclude_assets", [])
                        
                        if asset not in exclude:
                            if age_hours >= max_age:
                                logger.warning(f"⏰ {asset} position age: {age_hours:.1f}h (max: {max_age}h) - auto-closing")
                                should_close = True
                                close_reason = f"Position age limit ({max_age}h)"
                            elif age_hours >= warning_age:
                                logger.info(f"⚠️ {asset} position age: {age_hours:.1f}h (warning at {warning_age}h)")


            close_reason = ""
            tp_hit_label = None
            pnl_usd = 0.0
            pnl_pct = 0.0
            entry = pos["entry"]
            size = pos["size"]
            side = pos["side"]
            if side == "BUY":
                if current_price >= pos.get("tp3", float("inf")):
                    should_close = True
                    close_reason = "TP3 Hit"
                    tp_hit_label = "TP3"
                elif current_price >= pos.get("tp2", float("inf")) and pos.get("sl", 0) < pos.get("tp1", 0):
                    pos["sl"] = pos["tp1"]
                    await send_tp_hit(asset, "TP2", current_price, entry, chat_id)
                elif current_price >= pos.get("tp1", float("inf")) and pos.get("sl", 0) < entry and not pos.get("tp1_hit"):
                    # 🏹 PHASE 1: Partial Close 30% at TP1
                    close_size = size * float(config.get("smart_exit", {}).get("tp2_partial_pct", 0.35))
                    remaining_size = size - close_size
                    notional = close_size * current_price
                    
                    # Check minimum order size ($10)
                    if notional < 10:
                        logger.warning(f"⚠️ {asset} partial close skipped: ${notional:.2f} < $10 minimum")
                        pos["sl"] = entry * 1.002
                        pos["tp1_hit"] = True
                        await send_tp_hit(asset, "TP1 (skipped - too small)", current_price, entry, chat_id)
                    else:
                        try:
                            res = execute_hl_order(asset, "SELL", close_size, reduce_only=True)
                            if res.get("success"):
                                logger.info(f"✅ {asset} Partial TP1: Closed 30% ({close_size:.4f})")
                                pos["size"] = remaining_size
                                pos["sl"] = entry * 1.002
                                pos["tp1_hit"] = True
                                await send_tp_hit(asset, "TP1 (30% Closed)", current_price, entry, chat_id)
                            else:
                                raise Exception(res.get("error", "Unknown error"))
                        except Exception as e:
                            logger.error(f"❌ Partial close failed: {e}")
                            pos["sl"] = entry * 1.002
                            pos["tp1_hit"] = True
                            await send_tp_hit(asset, "TP1", current_price, entry, chat_id)
                # 🏹 PHASE 1: Chandelier Exit for TRENDING regime (after TP1)
                # 💰 DOLLAR-BASED RATCHET: Activate at $1+ net profit (not TP1-gated)
                _entry_r = pos.get("entry", 0)
                _size_r = pos.get("size", 0)
                _side_r = pos.get("side", "BUY")
                if _entry_r > 0 and _size_r > 0:
                    if _side_r == "BUY":
                        _gross = (current_price - _entry_r) * _size_r
                    else:
                        _gross = (_entry_r - current_price) * _size_r
                    _fee_pct = __import__("config_loader").get_config().get("execution", {}).get("taker_fee_pct", 0.00035)
                    _net = _gross - (_size_r * current_price * _fee_pct * 2)
                    _min_net = __import__("config_loader").get_config().get("execution", {}).get("ratchet_min_net_profit_usd", 1.0)
                    if _net >= _min_net and not pos.get("tp1_hit"):
                        _be_sl = _entry_r * 1.002 if _side_r == "BUY" else _entry_r * 0.998
                        if (_side_r == "BUY" and _be_sl > pos.get("sl", 0)) or (_side_r == "SELL" and _be_sl < pos.get("sl", float("inf"))):
                            old_sl = pos["sl"]
                            pos["sl"] = _be_sl
                            pos["tp1_hit"] = True
                            logger.info(f"💰 {asset} RATCHET: Net ${_net:.2f} >= ${_min_net}. SL ${old_sl:.4f} → ${_be_sl:.4f}")
                            await send_tp_hit(asset, f"RATCHET (net=${_net:.2f})", current_price, _entry_r, chat_id)
                if pos.get("tp1_hit") and str(pos.get("regime", "")).startswith("TRENDING"):
                    atr = pos.get("atr", 0)
                    if atr > 0:
                        chandelier_dist = atr * 3.5  # 3.5x ATR for breathing room
                        new_sl = current_price - chandelier_dist
                        if new_sl > pos.get("sl", 0) and new_sl > entry:
                            old_sl = pos["sl"]
                            pos["sl"] = new_sl
                            logger.info(f"📈 {asset} Chandelier Trail (TRENDING): ${old_sl:.4f} → ${new_sl:.4f}")

                elif current_price <= pos["sl"]:
                    # 🧠 Smart Learning Override
                    if not pos.get("sl_extended"):
                        try:
                            from core.meta_learner import get_meta_learner
                            meta = get_meta_learner()
                            regime = pos.get("regime", "RANGING")
                            strat = pos.get("strategy", "LLM")
                            weight = meta.get_weights(regime).get(strat, 0.0)
                            
                            if weight >= 0.20:  # 20% confidence threshold
                                original_risk = entry - pos["sl"]
                                pos["sl"] = pos["sl"] - (original_risk * 0.5)
                                pos["sl_extended"] = True
                                logger.info(f"🧠 Smart Defense (BUY): MetaLearner trusts {strat} in {regime} (Weight: {weight:.2f}). Widened SL to ${pos['sl']:.4f}")
                            else:
                                should_close = True
                                close_reason = "Stop Loss Hit"
                        except Exception as e:
                            logger.warning(f"MetaLearner check failed: {e}")
                            should_close = True
                            close_reason = "Stop Loss Hit"
                    else:
                        should_close = True
                        close_reason = "Stop Loss Hit"
            else:
                if current_price <= pos.get("tp3", 0):
                    should_close = True
                    close_reason = "TP3 Hit"
                    tp_hit_label = "TP3"
                elif current_price <= pos.get("tp2", float("inf")) and pos.get("sl", float("inf")) > pos.get("tp1", float("inf")):
                    pos["sl"] = pos["tp1"]
                    await send_tp_hit(asset, "TP2", current_price, entry, chat_id)
                elif current_price <= pos.get("tp1", float("inf")) and pos.get("sl", float("inf")) > entry and not pos.get("tp1_hit"):
                    # 🏹 PHASE 1: Partial Close 30% at TP1
                    close_size = size * float(config.get("smart_exit", {}).get("tp2_partial_pct", 0.35))
                    remaining_size = size - close_size
                    notional = close_size * current_price
                    
                    # Check minimum order size ($10)
                    if notional < 10:
                        logger.warning(f"⚠️ {asset} partial close skipped: ${notional:.2f} < $10 minimum")
                        pos["sl"] = entry * 0.998
                        pos["tp1_hit"] = True
                        await send_tp_hit(asset, "TP1 (skipped - too small)", current_price, entry, chat_id)
                    else:
                        try:
                            res = execute_hl_order(asset, "BUY", close_size, reduce_only=True)
                            if res.get("success"):
                                logger.info(f"✅ {asset} Partial TP1: Closed 30% ({close_size:.4f})")
                                pos["size"] = remaining_size
                                pos["sl"] = entry * 0.998
                                pos["tp1_hit"] = True
                                await send_tp_hit(asset, "TP1 (30% Closed)", current_price, entry, chat_id)
                            else:
                                raise Exception(res.get("error", "Unknown error"))
                        except Exception as e:
                            logger.error(f"❌ Partial close failed: {e}")
                            pos["sl"] = entry * 0.998
                            pos["tp1_hit"] = True
                            await send_tp_hit(asset, "TP1", current_price, entry, chat_id)
                # 🏹 PHASE 1: Chandelier Exit for TRENDING regime (after TP1)
                if pos.get("tp1_hit") and str(pos.get("regime", "")).startswith("TRENDING"):
                    atr = pos.get("atr", 0)
                    if atr > 0:
                        chandelier_dist = atr * 3.5
                        new_sl = current_price + chandelier_dist
                        if new_sl < pos.get("sl", float("inf")) and new_sl < entry:
                            old_sl = pos["sl"]
                            pos["sl"] = new_sl
                            logger.info(f"📉 {asset} Chandelier Trail (TRENDING): ${old_sl:.4f} → ${new_sl:.4f}")

                elif current_price >= pos["sl"]:
                    # 🧠 Smart Learning Override
                    if not pos.get("sl_extended"):
                        try:
                            from core.meta_learner import get_meta_learner
                            meta = get_meta_learner()
                            regime = pos.get("regime", "RANGING")
                            strat = pos.get("strategy", "LLM")
                            weight = meta.get_weights(regime).get(strat, 0.0)
                            
                            if weight >= 0.20:  # 20% confidence threshold
                                original_risk = pos["sl"] - entry
                                pos["sl"] = pos["sl"] + (original_risk * 0.5)
                                pos["sl_extended"] = True
                                logger.info(f"🧠 Smart Defense (SELL): MetaLearner trusts {strat} in {regime} (Weight: {weight:.2f}). Widened SL to ${pos['sl']:.4f}")
                            else:
                                should_close = True
                                close_reason = "Stop Loss Hit"
                        except Exception as e:
                            logger.warning(f"MetaLearner check failed: {e}")
                            should_close = True
                            close_reason = "Stop Loss Hit"
                    else:
                        should_close = True
                        close_reason = "Stop Loss Hit"

            # ============================================
            # TRAILING STOP-LOSS AFTER TP2 HIT
            # ============================================
            if pos.get("tp2_hit"):
                if side == "BUY":
                    # Trail stop at 50% of distance from TP2 to current price
                    tp2_price = pos.get("tp2", entry)
                    trail_distance = (current_price - tp2_price) * 0.5
                    new_sl = current_price - trail_distance
                    if new_sl > pos.get("sl", 0):
                        old_sl = pos["sl"]
                        pos["sl"] = new_sl
                        logger.info(f"📈 {asset} trailing SL: ${old_sl:.2f} → ${new_sl:.2f}")
                else:  # SELL
                    # Trail stop at 50% of distance from current price to TP2
                    tp2_price = pos.get("tp2", entry)
                    trail_distance = (tp2_price - current_price) * 0.5
                    new_sl = current_price + trail_distance
                    if new_sl < pos.get("sl", float("inf")):
                        old_sl = pos["sl"]
                        pos["sl"] = new_sl
                        logger.info(f"📉 {asset} trailing SL: ${old_sl:.2f} → ${new_sl:.2f}")

            if should_close:
                close_side = "SELL" if side == "BUY" else "BUY"
                result = execute_hl_order(coin=hl_assets.get(asset, asset), side=close_side, size=size)
                if not result.get("success"):
                    logger.error(f"❌ Failed to close {asset}: {result.get('error', 'unknown')}")
                    continue
                if side == "BUY":
                    pnl_usd = (current_price - entry) * size
                    pnl_pct = (current_price - entry) / entry * 100
                else:
                    pnl_usd = (entry - current_price) * size
                    pnl_pct = (entry - current_price) / entry * 100
                await send_closure(asset, side, entry, current_price, size, pnl_usd, pnl_pct, close_reason, chat_id, tp_hit=tp_hit_label)
                assets_to_remove.append(asset)
                updated_pnl = state.add_pnl(pnl_pct)
                logger.info(f"✅ {asset} closed: {close_reason} | PnL: ${pnl_usd:+,.2f} | Daily: {updated_pnl:.2f}%")
                
                # 📊 RECORD TRADE FOR PnL TRACKING & WIN RATE
                try:
                    state.record_closed_trade(
                        asset=asset,
                        side=side,
                        entry=entry,
                        exit_price=current_price,
                        size=size,
                        close_reason=close_reason,
                        strategy=pos.get("strategy", "LLM"),
                        regime=pos.get("regime", "RANGING")
                    )
                    logger.info(f"📊 Trade recorded: {asset} | {side} | PnL: ${pnl_usd:+,.2f} ({pnl_pct:+.2f}%)")
                except Exception as e:
                    logger.error(f"Failed to record trade: {e}")
                
                # SELF-LEARNING FEEDBACK LOOP
                try:
                    from core.meta_learner import get_meta_learner
                    meta = get_meta_learner()
                    strat_name = pos.get("strategy", "LLM")
                    regime = pos.get("regime", "RANGING")
                    meta.record_trade_outcome(strat_name, regime, pnl_pct)
                except Exception as e:
                    logger.error(f"MetaLearner update failed: {e}")
                
                # 📊 PHASE 2: EXIT ANALYTICS DATA COLLECTION
                try:
                    from core.exit_analytics import record_exit_analytics
                    
                    # Determine exit method
                    exit_method = "FIXED_TP"
                    if "TP" in close_reason:
                        exit_method = "FIXED_TP"
                    elif "Stop Loss" in close_reason or "Trailing" in close_reason or "Chandelier" in close_reason:
                        exit_method = "TRAILING"
                    
                    # Calculate hold time
                    opened_at_str = pos.get("opened_at")
                    if opened_at_str:
                        if isinstance(opened_at_str, str):
                            opened_at = datetime.fromisoformat(opened_at_str.replace('Z', '+00:00'))
                        else:
                            opened_at = opened_at_str
                        closed_at = datetime.now(timezone.utc)
                        hold_time_hours = (closed_at - opened_at).total_seconds() / 3600
                    else:
                        hold_time_hours = 0
                    
                    record_exit_analytics(
                        asset=asset,
                        regime=pos.get("regime", "RANGING"),
                        entry_strategy=pos.get("strategy", "LLM"),
                        exit_method=exit_method,
                        profit_pct=pnl_pct,
                        hold_time_hours=hold_time_hours,
                        entry_price=entry,
                        exit_price=current_price
                    )
                    logger.info(f"📊 Exit analytics recorded: {asset} | {exit_method} | {pnl_pct:+.2f}% | {hold_time_hours:.1f}h")
                except Exception as e:
                    logger.error(f"Exit analytics failed: {e}")
                halt_threshold = cfg.get("trading", {}).get("drawdown_halt_pct", -15.0)
                if is_drawdown_halted(halt_threshold):
                    from monitoring.alert_manager import send_drawdown_halt
                    await send_drawdown_halt(state.daily_pnl, halt_threshold, chat_id)
        except Exception as e:
            logger.error(f"❌ Error checking {asset}: {e}")
    for asset in assets_to_remove:
        state.OPEN_POSITIONS.pop(asset, None)

async def position_monitor_loop(chat_id: str) -> None:
    return  # DISABLED: Background task amputated
    cfg = get_config()
    interval = cfg.get("intervals", {}).get("position_monitor_sec", 60)
    logger.info(f"🔄 Position monitor (every {interval}s)")
    while True:
        try:
            if state.OPEN_POSITIONS:
                await check_and_close_positions(chat_id)
            else:
                # Also try to sync from exchange if state is empty
                from execution.hl_executor import HLExecutor
                executor = HLExecutor()
                exchange_positions = executor.get_open_positions()
                if exchange_positions:
                    for p in exchange_positions:
                        coin = p["coin"]
                        if coin not in state.OPEN_POSITIONS:
                            entry = float(p["entry_price"])
                            size = float(p["size"])
                            side = "BUY" if p["side"] == "long" else "SELL"
                            atr = entry * 0.02
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
                                "szi": float(p.get("position", {}).get("szi", size)),
                                "sl": sl,
                                "tp1": tp1,
                                "tp2": tp2,
                                "tp3": tp3,
                                "order_id": "synced",
                                "opened_at": datetime.now(timezone.utc),
                            }
                            logger.info(f"🔄 Synced {coin} from exchange to memory")
        except Exception as e:
            logger.error(f"❌ Position monitor error: {e}")
        await asyncio.sleep(interval)

async def quick_signal_scanner(chat_id: str) -> None:
    return  # DISABLED: Background task amputated
    cfg = get_config()
    interval = cfg.get("intervals", {}).get("quick_scanner_sec", 900)
    threshold = cfg.get("intervals", {}).get("big_move_threshold", 0.03)
    logger.info(f"🔄 Quick scanner (every {interval//60}min, {threshold*100:.0f}% threshold)")
    while True:
        await asyncio.sleep(interval)
        # Quick scanner logic – placeholder for now; you can add as needed
        pass

async def entry_scanner_loop(run_trade_fn, chat_id: str) -> None:
    return  # DISABLED: Background task amputated
    cfg = get_config()
    interval = cfg.get("intervals", {}).get("entry_scanner_sec", 1800)
    logger.info(f"🎯 Entry scanner (every {interval//60}min)")
    while True:
        await asyncio.sleep(interval)
        # Entry scanner logic – placeholder; actual signals are generated in full_analysis_loop
        # but we need to call run_trade when a signal appears. This is handled elsewhere.
        pass

async def full_analysis_loop(run_cycle_fn):
    return  # DISABLED: Background task amputated
    cfg = get_config()
    hours = cfg.get("intervals", {}).get("full_analysis_hours", 2)
    logger.info(f"🔄 Full analysis (every {hours}h)")
    while True:
        try:
            return  # DISABLED: Legacy scanner bypassed for Manual Grid/DCA mode
            logger.info("♻️ Full analysis cycle...")
            await run_cycle_fn()
            logger.info(f"💤 Sleeping {hours}h...")
        except Exception as e:
            logger.error(f"❌ Full analysis error: {e}")
        await asyncio.sleep(hours * 3600)


async def update_trailing_dca():
    """Background task: Update trailing DCA orders every 5 minutes."""
    while True:
        await asyncio.sleep(300)
        try:
            from core.state import OPEN_POSITIONS
            from core.dca_manager import DCAManager
            from execution.hl_executor import HLExecutor
            executor = HLExecutor()
            dca = DCAManager(executor)
            for asset, pos in OPEN_POSITIONS.items():
                dca_config = pos.get("dca")
                if dca_config and dca_config.get("trailing") and dca_config.get("enabled"):
                    # Check stabilization before updating trailing orders
                    if not dca.is_stabilized(asset):
                        continue
                    mids = executor.info.all_mids()
                    current_price = float(mids.get(asset, 0))
                    if current_price > 0:
                        result = await dca.update_trailing_orders(asset, dca_config, current_price)
                        if result["updated"] > 0:
                            logger.info(f"🔄 Updated {result['updated']} trailing DCA orders for {asset}")
        except Exception as e:
            logger.error(f"❌ Trailing DCA update failed: {e}")


async def monitor_dca_profit_targets():
    """Background task: Check DCA profit targets every 2 minutes."""
    while True:
        await asyncio.sleep(120)
        try:
            from core.state import OPEN_POSITIONS
            from core.dca_manager import DCAManager
            from execution.hl_executor import HLExecutor
            executor = HLExecutor()
            dca = DCAManager(executor)
            for asset, pos in OPEN_POSITIONS.items():
                dca_config = pos.get("dca")
                if dca_config and dca_config.get("profit_target_pct", 0) > 0 and dca_config.get("enabled"):
                    mids = executor.info.all_mids()
                    current_price = float(mids.get(asset, 0))
                    if current_price > 0:
                        recommendation = dca.check_profit_target(asset, dca_config, current_price)
                        if recommendation:
                            side = dca_config.get("direction", "LONG")
                            close_side = "SELL" if side == "LONG" else "BUY"
                            result = await dca.close_dca_position(asset, dca_config, close_side)
                            if result["base_closed"]:
                                OPEN_POSITIONS.pop(asset, None)
                                import core.state as _st
                                _st.save_state()
                                logger.info(f"🎯 Auto-closed {asset} at {recommendation['pnl_pct']:.2f}% profit")
        except Exception as e:
            logger.error(f"❌ DCA profit target monitor failed: {e}")


async def monitor_grid_bots():
    """Background task: Monitor GRID bots for fills and exit conditions.
    Only processes GRID:: namespaced positions — DCA unaffected."""
    while True:
        await asyncio.sleep(120)
        try:
            from core.state import OPEN_POSITIONS
            from core.grid_manager import GridManager, is_grid_position, grid_asset_from_key
            from execution.hl_executor import HLExecutor

            executor = HLExecutor()
            grid = GridManager(executor)

            for key in list(OPEN_POSITIONS.keys()):
                if not is_grid_position(key):
                    continue
                asset = grid_asset_from_key(key)
                config = OPEN_POSITIONS[key]
                if not config.get("enabled"):
                    continue

                mids = executor.info.all_mids()
                current_price = float(mids.get(asset, 0))
                if current_price <= 0:
                    continue

                exit_reason = grid.check_exit_conditions(asset, config, current_price)
                if exit_reason:
                    logger.info(f"🔲 GRID exit for {asset}: {exit_reason}")
                    grid.close_grid(asset, config)
                    OPEN_POSITIONS.pop(key, None)
                    import core.state as _st
                    _st.save_state()
                    continue

                fill_result = grid.monitor_grid_fills(asset, config)
                if fill_result["fills_detected"] > 0:
                    logger.info(
                        f"🔲 {asset}: {fill_result['fills_detected']} fills, "
                        f"{fill_result['tp_orders_placed']} TP orders"
                    )
        except Exception as e:
            logger.error(f"❌ GRID monitor failed: {e}")
