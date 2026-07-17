import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# ============================================================
# INJECT AUTONOMOUS SLOT HUNTER BACKGROUND TASK
# ============================================================
slot_hunter_code = '''
# ------------------------------------------------------------------
# Autonomous Slot Hunter — Fills free slots immediately (independent of analysis cycle)
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
            
            # Only act if a slot JUST opened (count decreased since last check)
            if _free_slots > 0 and _current_count < _last_slot_count:
                logger.info(f"🎯 SLOT HUNTER: {_free_slots} free slot(s) detected! Triggering immediate micro-scan...")
                
                _active_strat_id = _cfg_loader.get_config().get("execution", {}).get("active_strategy", "internal")
                _strat_cls = get_strategy_class(_active_strat_id) if _active_strat_id != "internal" else None
                
                # Scan top 4 assets by volume for immediate opportunity
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
                        
                        # Try native strategy first
                        if _strat_cls:
                            _ns = _strat_cls()
                            _signal, _conf = _ns.calculate_signal(_data)
                        
                        # Fallback to quick RSI check if no native signal
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
'''

if 'autonomous_slot_hunter' not in content:
    # Inject before the main() function
    content = content.replace('async def main() -> None:', slot_hunter_code + '\nasync def main() -> None:')
    
    # Add slot hunter to the asyncio.gather block
    content = content.replace(
        'full_analysis_loop(run_cycle),',
        'full_analysis_loop(run_cycle),\n        autonomous_slot_hunter(TELEGRAM_CHAT_ID),'
    )
    
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Injected Autonomous Slot Hunter background task")
else:
    print("ℹ️ Autonomous Slot Hunter already present")

print("\n🎉 Slot Hunter deployed.")
