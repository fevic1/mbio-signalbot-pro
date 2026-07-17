import os

print("🔍 Injecting Hard RSI Sanity Gate into main.py...")
main_path = 'main.py'
if os.path.exists(main_path):
    with open(main_path, 'r') as f:
        content = f.read()
        
    # The unbreakable RSI logic
    rsi_gate = """
            # 🛡️ HARD RSI SANITY GATE: Prevent directionally contradictory signals
            rsi_1d = float(data.get("1d", {}).get("rsi", 50.0))
            rsi_1h = float(data.get("1h", {}).get("rsi", 50.0))
            
            if "SELL" in signal and (rsi_1d < 40 or rsi_1h < 35):
                logger.warning(f"🛑 RSI GATE: Blocked SELL on {asset_name} (1D RSI={rsi_1d:.1f}, 1H RSI={rsi_1h:.1f}). Deeply oversold = BUY territory. Forcing HOLD.")
                signal = "HOLD"
                conf = 0
            elif "BUY" in signal and (rsi_1d > 65 or rsi_1h > 70):
                logger.warning(f"🛑 RSI GATE: Blocked BUY on {asset_name} (1D RSI={rsi_1d:.1f}, 1H RSI={rsi_1h:.1f}). Deeply overbought = SELL territory. Forcing HOLD.")
                signal = "HOLD"
                conf = 0
"""

    # Inject right before the final signal validation and Telegram dispatch
    target = 'if signal != "HOLD" and conf >= effective_min_conf:'
    if target in content and '🛡️ HARD RSI SANITY GATE' not in content:
        content = content.replace(target, rsi_gate + "\n            " + target)
        with open(main_path, 'w') as f:
            f.write(content)
        print("✅ Successfully injected Hard RSI Sanity Gate.")
    elif '🛡️ HARD RSI SANITY GATE' in content:
        print("ℹ️ RSI Gate already present.")
    else:
        print("❌ Could not find injection point in main.py.")
else:
    print("❌ main.py not found.")
