import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Check if the function exists anywhere in the file
if 'def init_telegram_bot' in content:
    print("ℹ️ init_telegram_bot exists but may be misnamed or unreachable.")
else:
    print("⚠️ init_telegram_bot is completely missing. Injecting restoration...")
    
    # Standard Telegram bot initializer for python-telegram-bot v20+
    init_func = '''
async def init_telegram_bot(token: str):
    """Initialize Telegram bot with all registered command handlers."""
    from telegram.ext import ApplicationBuilder, CommandHandler
    from monitoring.alert_manager import (
        cmd_positions, cmd_close, cmd_closeall, 
        cmd_ratchet, cmd_signal_source
    )
    
    application = ApplicationBuilder().token(token).build()
    
    # Register all command handlers
    application.add_handler(CommandHandler("positions", cmd_positions))
    application.add_handler(CommandHandler("close", cmd_close))
    application.add_handler(CommandHandler("closeall", cmd_closeall))
    application.add_handler(CommandHandler("ratchet", cmd_ratchet))
    application.add_handler(CommandHandler("signalsource", cmd_signal_source))
    
    logger.info("📱 Telegram commands active: /positions, /close, /closeall, /ratchet, /signalsource")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    return application
'''
    
    # Inject before the main() function
    if 'async def main()' in content:
        content = content.replace('async def main()', init_func + '\nasync def main()')
        with open(path, 'w') as f:
            f.write(content)
        print("✅ Injected init_telegram_bot before main().")
    else:
        print("❌ Could not find main() function anchor point.")

# Also verify the call site at line ~533
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'init_telegram_bot' in line and 'def ' not in line:
        print(f"  Call site found at line {i+1}: {line.strip()}")
