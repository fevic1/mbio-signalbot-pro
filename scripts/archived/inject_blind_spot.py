path = 'core/strategy_manager.py'
with open(path, 'r') as f:
    content = f.read()

old_block = '''                logger.warning("⚠️ Weak ensemble detected. Forcing HOLD to protect capital.")
                return "HOLD", 0, "ENSEMBLE"  # 🛡️ KILLED FALLBACK'''

new_block = '''                # 🛡️ PHASE 4: BLIND SPOT OVERRIDE (Deterministic Math Fallback)
                _rsi_1d = float(asset_data.get("1d", {}).get("rsi", 50))
                _rsi_1h = float(asset_data.get("1h", {}).get("rsi", 50))
                
                if _rsi_1d < 30 and _rsi_1h < 45:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} < 30 & 1H RSI={_rsi_1h:.1f} < 45. Deterministic BUY.")
                    return "BUY", 85, "DETERMINISTIC_MATH"
                elif _rsi_1d > 70 and _rsi_1h > 65:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} > 70 & 1H RSI={_rsi_1h:.1f} > 65. Deterministic SELL.")
                    return "SELL", 85, "DETERMINISTIC_MATH"
                else:
                    logger.warning("⚠️ Weak ensemble detected. Forcing HOLD to protect capital.")
                    return "HOLD", 0, "ENSEMBLE"  # 🛡️ KILLED FALLBACK'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Successfully injected Blind Spot Override into strategy_manager.py")
else:
    print("❌ Exact block not found. Check indentation.")
