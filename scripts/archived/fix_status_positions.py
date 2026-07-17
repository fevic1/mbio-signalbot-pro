with open('monitoring/alert_manager.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_cmd_status = False
found_positions_line = False

for i, line in enumerate(lines):
    # Detect when we enter cmd_status
    if 'async def cmd_status(' in line:
        in_cmd_status = True
    
    # Detect when we leave cmd_status (next function)
    if in_cmd_status and (line.strip().startswith('async def ') or line.strip().startswith('def ')) and 'cmd_status' not in line:
        in_cmd_status = False
    
    # Find the line that gets positions from state and replace it
    if in_cmd_status and 'positions = list(state.OPEN_POSITIONS.values())' in line:
        # Replace with live API call
        indent = len(line) - len(line.lstrip())
        new_lines.append(' ' * indent + '# Fetch live positions from API\n')
        new_lines.append(' ' * indent + 'positions, live_balance = await _fetch_live_positions()\n')
        new_lines.append(' ' * indent + 'if not positions:\n')
        new_lines.append(' ' * indent + '    positions = list(state.OPEN_POSITIONS.values())\n')
        new_lines.append(' ' * indent + 'if live_balance > 0:\n')
        new_lines.append(' ' * indent + '    balance = live_balance\n')
        found_positions_line = True
        continue
    
    new_lines.append(line)

with open('monitoring/alert_manager.py', 'w') as f:
    f.writelines(new_lines)

if found_positions_line:
    print("✅ Updated cmd_status to use live positions")
else:
    print("⚠️ Could not find the positions line to replace")
