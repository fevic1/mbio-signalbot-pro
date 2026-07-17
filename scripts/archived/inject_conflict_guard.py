import os

main_path = 'main.py'
if not os.path.exists(main_path):
    print("❌ main.py not found.")
    exit(1)

with open(main_path, 'r') as f:
    lines = f.readlines()

new_lines = []
injected = False

for i, line in enumerate(lines):
    new_lines.append(line)
    # Find the exact definition of the execution wrapper
    if line.strip().startswith('def _execute_trade(') and not injected:
        # Skip any empty lines or docstrings immediately following the def
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''")):
            new_lines.append(lines[j])
            j += 1
            # Handle multi-line docstrings
            if '"""' in lines[j-1] and lines[j-1].count('"""') == 1:
                while j < len(lines) and '"""' not in lines[j]:
                    new_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    new_lines.append(lines[j])
                    j += 1
                break
        
        if j < len(lines):
            # Calculate exact indentation based on the first actual line of code
            indent = len(lines[j]) - len(lines[j].lstrip())
            indent_str = ' ' * indent
            
            guard_code = [
                f"{indent_str}# 🛡️ DIRECTIONAL CONFLICT GUARD: Prevent Long/Short overlap\n",
                f"{indent_str}import core.state as _state\n",
                f"{indent_str}_existing_pos = _state.OPEN_POSITIONS.get(asset_name)\n",
                f"{indent_str}if _existing_pos:\n",
                f"{indent_str}    _existing_side = _existing_pos.get('side', 'BUY')\n",
                f"{indent_str}    _new_side = 'BUY' if 'BUY' in signal else 'SELL'\n",
                f"{indent_str}    if _existing_side != _new_side:\n",
                f"{indent_str}        logger.warning(f'🛑 CONFLICT GUARD: Blocked {{_new_side}} on {{asset_name}}. Already holding {{_existing_side}}.')\n",
                f"{indent_str}        return None\n",
                "\n"
            ]
            new_lines.extend(guard_code)
            injected = True

if injected:
    with open(main_path, 'w') as f:
        f.writelines(new_lines)
    print("✅ Successfully injected Directional Conflict Guard into _execute_trade().")
else:
    print("⚠️ Could not find _execute_trade definition to inject guard.")
