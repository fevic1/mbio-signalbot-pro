import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# ============================================================
# INJECT STRATEGY REGISTRY LOOKUP INTO ANALYSIS CYCLE
# ============================================================

# Find the start of the per-asset analysis loop
# We inject right after data extraction completes and before analyze_batch
target_marker = 'DEBUG: analyze_batch returned'

if 'STRATEGY REGISTRY ACTIVE' not in content:
    # Inject registry import at top of file
    if 'from core.strategy_registry import' not in content:
        content = content.replace(
            'from core.strategy_manager import StrategyManager',
            'from core.strategy_manager import StrategyManager\nfrom core.strategy_registry import get_strategy_class, list_strategies'
        )

    # Inject the active strategy resolution block BEFORE the analyze_batch call
    # We look for the pattern where analyze_batch is called and wrap it
    registry_block = '''
                    # 🔄 STRATEGY REGISTRY ACTIVE — Check for native strategy override
                    import config_loader as _cfg_loader
                    _active_strat_id = _cfg_loader.get_config().get("execution", {}).get("active_strategy", "internal")
                    _native_strategy = None
                    if _active_strat_id != "internal":
                        _strat_cls = get_strategy_class(_active_strat_id)
                        if _strat_cls:
                            _native_strategy = _strat_cls()
                            logger.info(f"📐 Using native strategy: {_active_strat_id} for {asset_name}")

                    if _native_strategy:
                        # Run native Python strategy — NO Groq API call
                        try:
                            _ns_signal, _ns_conf = _native_strategy.calculate_signal(data)
                            if _ns_signal != "HOLD" and _ns_conf >= 70:
                                sm_signal, sm_conf, sm_strategy = _ns_signal, _ns_conf, _active_strat_id
                                logger.info(f"📐 NATIVE SIGNAL: {asset_name} | {_ns_signal} ({_ns_conf}%) via {_active_strat_id}")
                            else:
                                sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
                                logger.info(f"📐 NATIVE HOLD: {asset_name} via {_active_strat_id}")
                        except Exception as _ns_err:
                            logger.error(f"❌ Native strategy error on {asset_name}: {_ns_err}")
                            sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
                    else:
'''

    # Find the analyze_batch call and wrap it in the else branch
    old_pattern = r'(DEBUG: analyze_batch returned:\s*\{)'
    match = re.search(old_pattern, content)

    if match:
        # Insert registry block before the analyze_batch debug line
        insert_pos = match.start()
        # Find the start of the line containing analyze_batch
        line_start = content.rfind('\n', 0, insert_pos) + 1
        indent = ' ' * 20  # Match typical indentation inside asset loop

        content = content[:line_start] + registry_block + '\n' + indent + '    # Fallback: AI Batch analysis (internal mode)\n' + indent + '    ' + content[line_start:]

        with open(path, 'w') as f:
            f.write(content)
        print("✅ Wired Strategy Registry into live analysis loop.")
    else:
        print("⚠️ Could not find analyze_batch marker. Manual wiring needed.")
else:
    print("ℹ️ Strategy Registry already wired.")

print("\n🎉 Final Wiring Complete.")
