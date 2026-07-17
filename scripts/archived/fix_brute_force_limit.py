import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Find the Brute Force execution block and inject a pre-flight YAML check
old_brute = 'if sm_signal != "HOLD" and asset_name not in state.OPEN_POSITIONS and len(state.OPEN_POSITIONS) < 3:'
new_brute = '''# 🛡️ BRUTE FORCE YAML PRE-FLIGHT CHECK
                        try:
                            _bf_max = __import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)
                        except Exception:
                            _bf_max = 3
                        if sm_signal != "HOLD" and asset_name not in state.OPEN_POSITIONS and len(state.OPEN_POSITIONS) < _bf_max:'''

if old_brute in content and 'BRUTE FORCE YAML PRE-FLIGHT' not in content:
    content = content.replace(old_brute, new_brute)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Injected YAML Pre-Flight Check into Brute Force Block.")
else:
    # Fallback: search for any variation of the brute force condition
    pattern = r'if sm_signal != ["\']HOLD["\'] and asset_name not in state\.OPEN_POSITIONS and len\(state\.OPEN_POSITIONS\) < \d+:'
    match = re.search(pattern, content)
    if match and 'BRUTE FORCE YAML PRE-FLIGHT' not in content:
        indent = ' ' * 24
        replacement = f'''{indent}# 🛡️ BRUTE FORCE YAML PRE-FLIGHT CHECK
{indent}try:
{indent}    _bf_max = __import__("config_loader").get_config().get("execution", {{}}).get("max_positions", 3)
{indent}except Exception:
{indent}    _bf_max = 3
{indent}if sm_signal != "HOLD" and asset_name not in state.OPEN_POSITIONS and len(state.OPEN_POSITIONS) < _bf_max:'''
        content = content[:match.start()] + replacement + content[match.end():]
        with open(path, 'w') as f:
            f.write(content)
        print("✅ Injected YAML Pre-Flight Check via regex fallback.")
    else:
        print("⚠️ Brute Force block not found or already patched.")
