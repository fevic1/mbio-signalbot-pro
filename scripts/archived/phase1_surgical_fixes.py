import os
import re

print("🔍 Starting Phase 1: Surgical Safety & Logic Fixes...\n")

# =========================================================
# 1. FIX REGIME DETECTION (core/regime.py)
# =========================================================
regime_path = 'core/regime.py'
if os.path.exists(regime_path):
    with open(regime_path, 'r') as f:
        content = f.read()
    
    # Standard Institutional ADX/ATR Math
    new_regime_logic = '''
def detect_regime(df_4h):
    """
    Institutional Regime Detection using standard 0-100 ADX and ATR%.
    """
    try:
        import pandas_ta as ta
        if df_4h is None or len(df_4h) < 20:
            return "RANGING"
            
        adx_df = ta.adx(df_4h["high"], df_4h["low"], df_4h["close"], length=14)
        if adx_df is None or "ADX_14" not in adx_df.columns:
            return "RANGING"
            
        adx = float(adx_df["ADX_14"].iloc[-1])
        atr = float(ta.atr(df_4h["high"], df_4h["low"], df_4h["close"], length=14).iloc[-1])
        atr_pct = atr / float(df_4h["close"].iloc[-1])
        
        if adx > 25:
            return "TRENDING"
        if atr_pct > 0.03:
            return "VOLATILE"
        return "RANGING"
    except Exception as e:
        return "RANGING"
'''
    
    # Replace the existing detect_regime function
    pattern = r'def detect_regime\(.*?\n(?:(?!def ).*\n)*'
    if re.search(pattern, content):
        content = re.sub(pattern, new_regime_logic + '\n', content, count=1)
        with open(regime_path, 'w') as f:
            f.write(content)
        print("✅ Fixed Regime Detection (Standardized ADX/ATR math).")
    else:
        print("⚠️ Could not find detect_regime function to replace. Manual review needed.")
else:
    print(f"❌ {regime_path} not found.")

# =========================================================
# 2. KILL WEAK-ENSEMBLE FALLBACK (core/strategy_manager.py)
# =========================================================
strat_path = 'core/strategy_manager.py'
if os.path.exists(strat_path):
    with open(strat_path, 'r') as f:
        content = f.read()
        
    # Find the dangerous fallback logic and neutralize it
    # We look for "weak ensemble" or "norm=" and force it to HOLD
    dangerous_patterns = [
        r'if\s+norm\s*<\s*[\d\.]+.*?using best strategy.*?\n',
        r'if\s+weak_ensemble.*?using best strategy.*?\n'
    ]
    
    fixed = False
    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            # Replace the fallback block with a strict HOLD
            content = re.sub(
                pattern, 
                'if True: # 🛡️ KILLED WEAK FALLBACK: Force HOLD on low consensus\n                return "HOLD", 0, "ENSEMBLE"\n', 
                content, 
                flags=re.IGNORECASE | re.DOTALL
            )
            fixed = True
            
    if fixed:
        with open(strat_path, 'w') as f:
            f.write(content)
        print("✅ Killed Weak-Ensemble Fallback (Forces HOLD on low consensus).")
    else:
        print("ℹ️ Weak fallback pattern not found or already neutralized.")
else:
    print(f"❌ {strat_path} not found.")

# =========================================================
# 3. DIRECTIONAL CONFLICT GUARD (main.py)
# =========================================================
main_path = 'main.py'
if os.path.exists(main_path):
    with open(main_path, 'r') as f:
        content = f.read()
        
    guard_code = '''
            # 🛡️ DIRECTIONAL CONFLICT GUARD: Prevent Long/Short overlap
            existing_pos = state.OPEN_POSITIONS.get(asset_name)
            if existing_pos:
                existing_side = existing_pos.get("side", "BUY")
                if (existing_side == "BUY" and "SELL" in signal) or (existing_side == "SELL" and "BUY" in signal):
                    logger.warning(f"🛑 CONFLICT GUARD: Blocked {signal} on {asset_name}. Already holding {existing_side}. Close manually first.")
                    continue
'''
    
    # Inject right before the execution block (usually where it checks max positions)
    target = 'if signal != "HOLD" and conf >= effective_min_conf:'
    if target in content and '🛡️ DIRECTIONAL CONFLICT GUARD' not in content:
        content = content.replace(target, guard_code + "\n            " + target)
        with open(main_path, 'w') as f:
            f.write(content)
        print("✅ Injected Directional Conflict Guard into main.py.")
    elif '🛡️ DIRECTIONAL CONFLICT GUARD' in content:
        print("ℹ️ Conflict Guard already present.")
    else:
        print("⚠️ Could not find execution injection point in main.py.")
else:
    print(f"❌ {main_path} not found.")

print("\n🎉 Phase 1 Complete. The bot is now mathematically grounded and protected from rogue strategies.")
