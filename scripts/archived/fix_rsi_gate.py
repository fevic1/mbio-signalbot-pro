import sys

with open('main.py', 'r') as f:
    content = f.read()

gate = """
        # 🛡️ HARD RSI SANITY GATE: Prevent directionally contradictory signals
        rsi_1d = float(data.get("1d", {}).get("rsi", 50.0))
        rsi_1h = float(data.get("1h", {}).get("rsi", 50.0))
        if "SELL" in signal and (rsi_1d < 40 or rsi_1h < 35):
            logger.warning(f"🛑 RSI GATE: Blocked SELL on {asset_name} (1D={rsi_1d:.1f}, 1H={rsi_1h:.1f}). Oversold = BUY. Forcing HOLD.")
            signal, conf = "HOLD", 0
        elif "BUY" in signal and (rsi_1d > 65 or rsi_1h > 70):
            logger.warning(f"🛑 RSI GATE: Blocked BUY on {asset_name} (1D={rsi_1d:.1f}, 1H={rsi_1h:.1f}). Overbought = SELL. Forcing HOLD.")
            signal, conf = "HOLD", 0
"""

target = 'logger.warning(f"StrategyManager failed: {e}")'
if target in content and '🛡️ HARD RSI SANITY GATE' not in content:
    content = content.replace(target, target + gate)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ Successfully injected Hard RSI Sanity Gate into main.py.")
elif '🛡️ HARD RSI SANITY GATE' in content:
    print("ℹ️ RSI Gate already present.")
else:
    print("❌ Could not find injection point.")
    sys.exit(1)
