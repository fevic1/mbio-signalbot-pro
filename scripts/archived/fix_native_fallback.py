path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Replace the gating logic with supplementary logic
old_block = '''            if _native_strategy:
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

new_block = '''            # Get AI Batch signal FIRST (always available as baseline)
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

if old_block in content:
    content = content.replace(old_block, new_block)

    # Also remove the duplicate AI result extraction that was inside the else block
    # since we now extract it BEFORE the native strategy check
    dup_extract = '''            # Fallback: AI Batch analysis (internal mode)
                result = results.get(asset_name) or {}
                signal = result.get("signal", "HOLD")
                conf = result.get("confidence", 50)
                reason = result.get("reasoning", "")'''
    content = content.replace(dup_extract, '            # AI signal already extracted above')

    with open(path, 'w') as f:
        f.write(content)
    print("✅ Fixed: Native strategy now supplements AI instead of gating it")
else:
    print("⚠️ Could not find exact old block. Manual review needed.")
