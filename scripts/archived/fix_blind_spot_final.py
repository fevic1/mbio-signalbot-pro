import os

path = 'core/strategy_manager.py'
with open(path, 'r') as f:
    content = f.read()

# Target the exact final log line of the ensemble vote
target = 'logger.info(f"🏆 Ensemble Vote: {final_signal} | Winning Strategy: {winner} | Consensus Score: {conf}%")'

override = '''        # 🚀 PHASE 4: BLIND SPOT OVERRIDE (Deterministic Dip-Buyer)
        if final_signal == "HOLD" or conf < 60:
            try:
                _rsi_1d = float(asset_data.get('1d', {}).get('rsi', 50))
                _rsi_1h = float(asset_data.get('1h', {}).get('rsi', 50))
                if _rsi_1d < 35 and _rsi_1h < 55:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} < 35 & 1H RSI={_rsi_1h:.1f} < 55. Deterministic BUY.")
                    final_signal, conf, winner = "BUY", 85, "DETERMINISTIC_MATH"
                elif _rsi_1d > 70 and _rsi_1h > 65:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} > 70 & 1H RSI={_rsi_1h:.1f} > 65. Deterministic SELL.")
                    final_signal, conf, winner = "SELL", 85, "DETERMINISTIC_MATH"
            except Exception:
                pass
'''

if target in content and 'PHASE 4: BLIND SPOT OVERRIDE' not in content:
    content = content.replace(target, override + target)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Successfully injected Blind Spot Override at the final decision gate.")
else:
    print("⚠️ Target log line not found or override already present.")
