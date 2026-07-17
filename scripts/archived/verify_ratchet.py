import re

# 1. Check alert_manager.py
am_path = 'monitoring/alert_manager.py'
with open(am_path, 'r') as f:
    am_content = f.read()

if 'def cmd_ratchet' not in am_content:
    print("⚠️ cmd_ratchet missing in alert_manager.py. Re-injecting...")
    ratchet_code = """

async def cmd_ratchet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from core.profit_ratchet import toggle_ratchet
    new_state = toggle_ratchet()
    status = "🟢 ON" if new_state else "🔴 OFF"
    msg = f"🏹 *Profit Ratchet*\\n━━━━━━━━━━━━━━━━━━━━\\nStatus: {status}\\n\\n"
    if new_state:
        msg += "Now securing partial profit on all open positions."
    else:
        msg += "Ratchet disabled. Relying on standard TP/SL."
    await update.message.reply_text(msg, parse_mode="Markdown")
"""
    with open(am_path, 'a') as f:
        f.write(ratchet_code)
    print("✅ Re-injected cmd_ratchet.")
else:
    print("✅ cmd_ratchet is intact in alert_manager.py.")

# 2. Check main.py
main_path = 'main.py'
with open(main_path, 'r') as f:
    main_content = f.read()

ratchet_handler_missing = 'CommandHandler("ratchet"' not in main_content and "CommandHandler('ratchet'" not in main_content
import_missing = 'cmd_ratchet' not in main_content

if ratchet_handler_missing or import_missing:
    print("⚠️ /ratchet handler or import missing in main.py. Re-wiring...")
    
    # Fix import
    if import_missing:
        import_match = re.search(r'(from monitoring\.alert_manager import [^\n]+)', main_content)
        if import_match:
            old_imp = import_match.group(1)
            new_imp = old_imp.rstrip() + ', cmd_ratchet'
            main_content = main_content.replace(old_imp, new_imp)
            
    # Fix handler registration
    if ratchet_handler_missing:
        handler_match = re.search(r'(application\.add_handler\(CommandHandler\([^)]+\)\))', main_content)
        if handler_match:
            main_content = main_content.replace(
                handler_match.group(1),
                handler_match.group(1) + '\n    application.add_handler(CommandHandler("ratchet", cmd_ratchet))'
            )
            
    with open(main_path, 'w') as f:
        f.write(main_content)
    print("✅ Re-wired /ratchet in main.py.")
else:
    print("✅ /ratchet is fully wired in main.py.")
