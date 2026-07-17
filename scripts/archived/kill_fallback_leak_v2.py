import os

path = 'core/strategy_manager.py'
if not os.path.exists(path):
    print(f"❌ {path} not found.")
    exit(1)

with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
patched_count = 0

for line in lines:
    new_lines.append(line)
    # Look for the exact log message that indicates the fallback is triggering
    if 'using best strategy' in line and ('logger' in line or 'print' in line or 'warning' in line.lower()):
        # Calculate exact indentation of the current line
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        # Inject the immediate return on the very next line
        new_lines.append(f'{indent_str}return "HOLD", 0, "ENSEMBLE"  # 🛡️ KILLED FALLBACK\n')
        patched_count += 1

if patched_count > 0:
    with open(path, 'w') as f:
        f.writelines(new_lines)
    print(f"✅ Successfully injected {patched_count} HOLD return(s) after 'using best strategy'.")
else:
    print("⚠️ String 'using best strategy' not found in logger calls.")
    print("Locating actual string in file...")
    os.system(f"grep -n 'using best strategy' {path}")
