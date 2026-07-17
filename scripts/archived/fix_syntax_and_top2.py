import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Fix the broken def line
broken_def = 'def (_cycle_executions >= 2 and logger.info("🛑 TOP 2 LIMIT: Skipping further executions this cycle.")) or _execute_trade(asset_name, signal, entry_price, sl, tp1, tp2, tp3, size, strategy="AI ensemble", regime="RANGING"):'
correct_def = 'def _execute_trade(asset_name, signal, entry_price, sl, tp1, tp2, tp3, size, strategy="AI ensemble", regime="RANGING"):'

if broken_def in content:
    content = content.replace(broken_def, correct_def)
    print("✅ Fixed broken def line via literal match.")
else:
    # Fallback regex in case of slight whitespace differences
    content = re.sub(
        r'def \(_cycle_executions.*?or _execute_trade\((.*?)\):',
        r'def _execute_trade(\1):',
        content
    )
    print("✅ Fixed broken def line via regex.")

# 2. Remove broken _cycle_executions counter injections to prevent UnboundLocalError
content = re.sub(r'[ \t]*_cycle_executions \+= 1.*?\n', '', content)
content = re.sub(r'[ \t]*_cycle_executions = 0.*?\n', '', content)
print("✅ Removed broken cycle counter injections.")

# 3. Inject a safe Top 2 limit at the top of _execute_trade
if '🛑 TOP 2 LIMIT: Already holding' not in content:
    injection = """    # 🛡️ TOP 2 LIMIT: Prevent over-leveraging during market crashes
    import core.state as _state
    if len(_state.OPEN_POSITIONS) >= 2:
        logger.info(f"🛑 TOP 2 LIMIT: Already holding {len(_state.OPEN_POSITIONS)} positions. Skipping {asset_name}.")
        return None
"""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith('def _execute_trade('):
            new_lines.append(injection)
            
    content = '\n'.join(new_lines)
    print("✅ Injected safe Top 2 limit into _execute_trade.")

with open(path, 'w') as f:
    f.write(content)
