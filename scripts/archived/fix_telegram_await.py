import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Remove await from the init call
content = re.sub(
    r'await\s+init_telegram_bot\(TELEGRAM_BOT_TOKEN\)',
    'application = init_telegram_bot(TELEGRAM_BOT_TOKEN)',
    content
)

# 2. Ensure handlers are registered AFTER init and polling is started
# Find the line right after the init call and inject handler registration + polling
handler_block = '''
    # Register Telegram command handlers
    from telegram.ext import CommandHandler
    from monitoring.alert_manager import cmd_positions, cmd_close, cmd_closeall, cmd_ratchet, cmd_signal_source
    
    application.add_handler(CommandHandler("positions", cmd_positions))
    application.add_handler(CommandHandler("close", cmd_close))
    application.add_handler(CommandHandler("closeall", cmd_closeall))
    application.add_handler(CommandHandler("ratchet", cmd_ratchet))
    application.add_handler(CommandHandler("signalsource", cmd_signal_source))
    
    logger.info("📱 Telegram commands active: /positions, /close, /closeall, /ratchet, /signalsource")
    
    # Start polling (async)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
'''

# Inject after the init call if not already present
if 'application.add_handler(CommandHandler("positions"' not in content:
    content = content.replace(
        'application = init_telegram_bot(TELEGRAM_BOT_TOKEN)',
        'application = init_telegram_bot(TELEGRAM_BOT_TOKEN)' + handler_block
    )
    print("✅ Removed await, injected handler registration + polling start.")
else:
    # Handlers exist but await might still be there
    content = re.sub(
        r'await\s+init_telegram_bot\(TELEGRAM_BOT_TOKEN\)',
        'application = init_telegram_bot(TELEGRAM_BOT_TOKEN)',
        content
    )
    print("✅ Removed stale await from init call.")

with open(path, 'w') as f:
    f.write(content)

print("🎉 Telegram boot sequence fixed.")
