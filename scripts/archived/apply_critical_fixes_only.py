path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# FIX 1: Native Strategy Supplementary Logic (No import changes)
old_native_block = '''            if _native_strategy:
                try:
                    _ns_signal, _ns_conf = _native_strategy.calculate_signal(data)
                    if _ns_signal != "HOLD" and _ns_conf >= 70:
                        sm_signal, sm_conf, sm_strategy = _ns_signal, _ns_conf, _active_strat_id
                        logger.info(f"📐 NATIVE SIGNAL: {asset_name} | {_ns_signal} ({_ns_conf}%) via {_active_strat_id}")
                    else:
                        sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
                except Exception as _ns_err:
                    logger.error(f"❌ Native strategy error on {asset_name}: {_ns_err}")
                    sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
            else:'''

new_native_block = '''            # Get AI Batch signal FIRST (always available as baseline)
            result = results.get(asset_name) or {}
            signal = result.get("signal", "HOLD")
            conf = result.get("confidence", 50)
            reason = result.get("reasoning", "")

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
            # If no native strategy configured, AI signal already set above'''

if old_native_block in content:
    content = content.replace(old_native_block, new_native_block)
    # Remove duplicate AI extraction inside else block
    dup_ai = '''            # Fallback: AI Batch analysis (internal mode)
                result = results.get(asset_name) or {}
                signal = result.get("signal", "HOLD")
                conf = result.get("confidence", 50)
                reason = result.get("reasoning", "")'''
    content = content.replace(dup_ai, '            # AI signal already extracted above')
    print("✅ Fix 1 Applied: Native strategy now supplements AI")
else:
    print("⚠️ Fix 1: Native block not found (may already be fixed)")

# FIX 2: Leverage-Aware SL in run_trade
old_sl_calc = '''    sl_atr_mult = tp.get("sl_atr_multiplier", 1.5)
    min_atr = tp.get("min_atr_pct", 0.02)
    sl_distance = entry_price * min_atr * sl_atr_mult'''

new_sl_calc = '''    sl_atr_mult = tp.get("sl_atr_multiplier", 1.5)
    min_atr = tp.get("min_atr_pct", 0.02)
    sl_distance = entry_price * min_atr * sl_atr_mult

    # 🛡️ LEVERAGE GUARD: SL must never exceed safe margin distance
    _leverage = float(data.get("1h", {}).get("leverage", 20))
    _max_sl_pct = (1.0 / _leverage) * 0.4  # 40% of margin as max SL buffer
    _max_sl_distance = entry_price * _max_sl_pct
    if sl_distance > _max_sl_distance:
        logger.warning(f"⚠️ {asset_name} SL ${sl_distance:.2f} exceeds safe limit ${_max_sl_distance:.2f} at {_leverage}x. Capping.")
        sl_distance = _max_sl_distance'''

if old_sl_calc in content:
    content = content.replace(old_sl_calc, new_sl_calc)
    print("✅ Fix 2 Applied: Leverage-aware SL cap in run_trade")
else:
    print("⚠️ Fix 2: SL calc not found (may already be fixed)")

with open(path, 'w') as f:
    f.write(content)
