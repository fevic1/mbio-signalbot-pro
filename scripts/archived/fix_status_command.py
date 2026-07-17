with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# Find and update the cmd_status function to use live positions
# Look for the line that says "positions = list(state.OPEN_POSITIONS.values())"
# and replace it with a call to _fetch_live_positions()

old_status_line = "positions = list(state.OPEN_POSITIONS.values())"
new_status_code = """# Fetch live positions from API
    positions, live_balance = await _fetch_live_positions()
    if not positions:
        positions = list(state.OPEN_POSITIONS.values())
    if live_balance > 0:
        balance = live_balance"""

content = content.replace(old_status_line, new_status_code)

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Updated /status command to use live positions")
