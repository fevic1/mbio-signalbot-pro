import re

# === PATCH 1: main.py — Wire application to alert_manager ===
path_main = 'main.py'
with open(path_main, 'r') as f:
    content = f.read()

# Find "await application.initialize()" and inject wiring after it
old_init = '    await application.initialize()'
new_init = '''    await application.initialize()
    # Wire Telegram bot instance to alert_manager for notifications
    import monitoring.alert_manager as _am
    _am._application = application
    _am.set_bot_ready(True)
    logger.info("📱 Telegram bot wired to alert_manager")'''

if old_init in content and '_am._application = application' not in content:
    content = content.replace(old_init, new_init, 1)
    with open(path_main, 'w') as f:
        f.write(content)
    print("✅ main.py: Telegram bot wired to alert_manager")
elif '_am._application = application' in content:
    print("ℹ️ main.py: Wiring already present")
else:
    print("⚠️ main.py: Could not find 'await application.initialize()'")

# === PATCH 2: alert_manager.py — Harden the guard ===
path_am = 'monitoring/alert_manager.py'
with open(path_am, 'r') as f:
    am_content = f.read()

# Ensure _application module variable exists
if '_application = None' not in am_content and '_application=' not in am_content.split('def ')[0]:
    # Add after imports
    last_import = list(re.finditer(r'^from .+ import .+$|^import .+$', am_content, re.MULTILINE))
    if last_import:
        insert_pos = last_import[-1].end()
        am_content = am_content[:insert_pos] + '\n\n# Telegram bot instance — set by main.py after initialize()\n_application = None\n_bot_ready = False\n' + am_content[insert_pos:]
        print("✅ alert_manager.py: Added _application and _bot_ready module variables")

# Ensure set_bot_ready function exists
if 'def set_bot_ready' not in am_content:
    am_content += '\n\ndef set_bot_ready(ready: bool = True):\n    """Call after application.initialize() completes."""\n    global _bot_ready\n    _bot_ready = ready\n'
    print("✅ alert_manager.py: Added set_bot_ready() function")

# Harden send_signal guard
for func_name in ['send_signal', 'send_execution', 'send_tp_hit']:
    pattern = rf'(async def {func_name}\([^)]*\):)'
    match = re.search(pattern, am_content)
    if match:
        # Check if guard already exists within next 5 lines
        after = am_content[match.end():match.end()+300]
        if '_application' not in after.split('\n')[1:6]:
            guard = f'\n    global _application, _bot_ready\n    if not _bot_ready or _application is None:\n        return'
            am_content = am_content[:match.end()] + guard + am_content[match.end():]
            print(f"✅ alert_manager.py: Hardened guard in {func_name}()")

with open(path_am, 'w') as f:
    f.write(am_content)

print("\n🎉 All Telegram initialization patches applied.")
