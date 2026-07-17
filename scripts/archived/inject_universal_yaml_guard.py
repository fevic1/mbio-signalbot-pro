import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# The Universal Guard that reads the YAML dynamically
guard_code = """    # 🛡️ UNIVERSAL YAML POSITION LIMIT GUARD
    import core.state as _state
    try:
        _max_pos = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
    except Exception:
        _max_pos = 3
        
    if len(_state.OPEN_POSITIONS) >= _max_pos and asset_name not in _state.OPEN_POSITIONS:
        logger.info(f"🛑 YAML LIMIT: Max positions ({_max_pos}) reached. Blocking {asset_name} execution.")
        return None
"""

# Find the exact definition of the execution wrapper
pattern = r'(def _execute_trade\([^)]+\):[\s\n]*)(?!\s*# 🛡️ UNIVERSAL YAML)'
match = re.search(pattern, content)

if match and 'UNIVERSAL YAML POSITION LIMIT GUARD' not in content:
    # Inject immediately after the def line (and any docstrings)
    insert_pos = match.end()
    content = content[:insert_pos] + '\n' + guard_code + content[insert_pos:]
    
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Injected Universal YAML Guard into _execute_trade().")
else:
    print("ℹ️ Universal YAML Guard already present or target missed.")
