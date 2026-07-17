import os

print("🔍 Starting Phase 3: Rate-Limit Shield & Hunter Upgrade...\n")

# =========================================================
# 1. LLM RATE-LIMIT SHIELD (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
if os.path.exists(llm_path):
    with open(llm_path, 'r') as f:
        content = f.read()
        
    shield_code = """
        # 🛡️ ARCHITECTURAL FIX: Rate-Limit Shield (Stagger & Cache)
        import time
        import hashlib
        time.sleep(0.8)  # Stagger requests to prevent Groq/Cerebras 429 burst
        
        # Cache LLM reasoning for 15 minutes to avoid redundant API calls
        _cache_key = hashlib.md5(f"{data.get('symbol', '')}_{data.get('1h', {}).get('rsi', '')}".encode()).hexdigest()
        if not hasattr(self, '_llm_cache'): self._llm_cache = {}
        if _cache_key in self._llm_cache and (time.time() - self._llm_cache[_cache_key]['ts']) < 900:
            logger.info(f"💾 LLM CACHE: Using cached reasoning for {data.get('symbol', 'UNKNOWN')}")
            # Return cached tuple (signal, confidence, reasoning)
            return self._llm_cache[_cache_key]['data']
"""
    if 'ARCHITECTURAL FIX: Rate-Limit Shield' not in content:
        target = 'GROQ_API_KEY found'
        if target in content:
            content = content.replace(f'logger.info("{target}', shield_code + f'\n        logger.info("{target}')
            
            # We also need to save to cache at the end of the function. 
            # We'll inject a cache save right before the final return.
            cache_save = """
        # 🛡️ Save to LLM Cache
        if hasattr(self, '_llm_cache'):
            self._llm_cache[_cache_key] = {'ts': time.time(), 'data': (signal, confidence, reasoning) if 'reasoning' in locals() else (signal, confidence, "")}
"""
            content = content.replace('return signal, confidence', cache_save + '\n        return signal, confidence')
            content = content.replace('return "HOLD", 0', cache_save + '\n        return "HOLD", 0')
            
            with open(llm_path, 'w') as f:
                f.write(content)
            print("✅ Injected Rate-Limit Shield & Cache into LLM Strategy.")
        else:
            print("⚠️ Could not find LLM injection point.")
else:
    print(f"❌ {llm_path} not found.")

# =========================================================
# 2. REAL HUNTER PROTOCOL (monitoring/position_tracker.py)
# =========================================================
tracker_path = 'monitoring/position_tracker.py'
if os.path.exists(tracker_path):
    with open(tracker_path, 'r') as f:
        content = f.read()
        
    hunter_logic = """
            # 🛡️ ARCHITECTURAL FIX: Real Hunter Protocol (Capital Efficiency Check)
            if _age_hrs > 24.0 and abs(_pnl_pct) < 1.0:
                logger.warning(f"🏹 HUNTER: {_asset} is STAGNANT (Age: {_age_hrs:.1f}h, PnL: {_pnl_pct:+.2f}%). Consider manual closure to free margin.")
            elif _pnl_pct < -5.0:
                logger.warning(f"🏹 HUNTER: {_asset} is BLEEDING (PnL: {_pnl_pct:+.2f}%). Approaching critical drawdown.")
"""
    if 'ARCHITECTURAL FIX: Real Hunter Protocol' not in content:
        # Inject right before the telemetry log so it evaluates first
        content = content.replace(
            'logger.info(f"📊 TELEMETRY:',
            hunter_logic + '\n            logger.info(f"📊 TELEMETRY:'
        )
        with open(tracker_path, 'w') as f:
            f.write(content)
        print("✅ Injected Real Hunter Protocol into Position Tracker.")
else:
    print(f"❌ {tracker_path} not found.")

print("\n🎉 Phase 3 Speed & Hunter Rectification Complete.")
