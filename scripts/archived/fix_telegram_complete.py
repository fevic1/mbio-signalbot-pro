import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Restore module-level imports for ALL telegram commands
required_imports = [
    'cmd_positions', 'cmd_close', 'cmd_closeall', 
    'cmd_ratchet', 'cmd_signal_source'
]

# Check current import state
import_match = re.search(r'from monitoring\.alert_manager import ([^\n]+)', content)
if import_match:
    current_imports = import_match.group(1)
    missing = [imp for imp in required_imports if imp not in current_imports]
    if missing:
        new_import_line = f"from monitoring.alert_manager import {current_imports.rstrip().rstrip(',')}, {', '.join(missing)}"
        content = content.replace(import_match.group(0), new_import_line)
        print(f"✅ Added missing imports: {', '.join(missing)}")
    else:
        print("ℹ️ All command imports already present.")
else:
    # No import exists at all - add fresh one
    fresh_import = "from monitoring.alert_manager import cmd_positions, cmd_close, cmd_closeall, cmd_ratchet, cmd_signal_source\n"
    # Insert after other monitoring imports or at top of file
    content = fresh_import + content
    print("✅ Added fresh alert_manager import line.")

# 2. Fix the un-awaited coroutine call
content = re.sub(
    r'^(\s*)init_telegram_bot\(TELEGRAM_BOT_TOKEN\)',
    r'\1await init_telegram_bot(TELEGRAM_BOT_TOKEN)',
    content,
    flags=re.MULTILINE
)
print("✅ Fixed await on init_telegram_bot call.")

# 3. Remove duplicate handler registrations inside init_telegram_bot
# since they're already registered in main() after the await
# This prevents double-registration warnings
content = re.sub(
    r'(async def init_telegram_bot.*?return application)',
    '',
    content,
    flags=re.DOTALL
)

# 4. Replace the async init function with a simple synchronous version
# that just returns the ApplicationBuilder (handlers registered in main())
simple_init = '''
def init_telegram_bot(token: str):
    """Initialize Telegram bot application."""
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(token).build()
    logger.info("📱 Telegram bot initialized")
    return application
'''

# Insert before main()
if 'def init_telegram_bot' not in content:
    content = content.replace('async def main()', simple_init + '\nasync def main()')
    print("✅ Injected synchronous init_telegram_bot.")

with open(path, 'w') as f:
    f.write(content)

print("\n🎉 Telegram restoration complete.")
