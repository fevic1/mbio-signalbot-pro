import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Remove the DUPLICATE "TOP 2 LIMIT" check in _execute_trade
content = re.sub(
    r'\n\s*# 🛡️ TOP 2 LIMIT: Prevent over-leveraging.*?return None\n',
    '\n',
    content,
    flags=re.DOTALL
)
print("✅ Removed duplicate TOP 2 LIMIT check from _execute_trade")

# 2. Fix run_trade() to use execution.max_positions instead of trading.max_open_positions
content = re.sub(
    r'max_pos\s*=\s*t\.get\(\s*"max_open_positions"\s*,\s*\d+\s*\)',
    'max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)',
    content
)
print("✅ Fixed run_trade() to use execution.max_positions from YAML")

# 3. Ensure the Universal YAML Guard is the ONLY gate in _execute_trade
# Verify it exists
if 'UNIVERSAL YAML POSITION LIMIT GUARD' not in content:
    print("⚠️ Universal YAML Guard missing! Re-injecting...")
    guard = '''    # 🛡️ UNIVERSAL YAML POSITION LIMIT GUARD
    import core.state as _state
    try:
        _max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
    except Exception:
        _max_pos = 3
    if len(_state.OPEN_POSITIONS) >= _max_pos and asset_name not in _state.OPEN_POSITIONS:
        logger.info(f"🛑 YAML LIMIT: Max positions ({_max_pos}) reached. Blocking {asset_name} execution.")
        return None
'''
    content = content.replace(
        'def _execute_trade(asset_name, signal, entry_price, sl, tp1, tp2, tp3, size, strategy="AI ensemble", regime="RANGING"):',
        'def _execute_trade(asset_name, signal, entry_price, sl, tp1, tp2, tp3, size, strategy="AI ensemble", regime="RANGING"):\n' + guard
    )
    print("✅ Re-injected Universal YAML Guard")
else:
    print("✅ Universal YAML Guard already present")

with open(path, 'w') as f:
    f.write(content)

print("\n🎉 Position limit consolidation complete.")
