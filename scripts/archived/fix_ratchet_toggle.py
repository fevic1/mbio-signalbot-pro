import re

# 1. Re-add cmd_ratchet to alert_manager.py
alert_path = 'monitoring/alert_manager.py'
with open(alert_path, 'r') as f:
    content = f.read()

if 'def cmd_ratchet' not in content:
    ratchet_cmd = '''

# ============================================================
# 🏹 FEE-AWARE RATCHET TOGGLE
# ============================================================
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
'''
    with open(alert_path, 'a') as f:
        f.write(ratchet_cmd)
    print("✅ Re-added cmd_ratchet to alert_manager.py")
else:
    print("ℹ️ cmd_ratchet already in alert_manager.py")

# 2. Register the handler in main.py
main_path = 'main.py'
with open(main_path, 'r') as f:
    main_content = f.read()

if 'cmd_ratchet' not in main_content:
    # Add to import statement
    import_match = re.search(r'from monitoring\.alert_manager import ([^\n]+)', main_content)
    if import_match:
        old_import_line = import_match.group(0)
        new_import_line = old_import_line + ', cmd_ratchet'
        main_content = main_content.replace(old_import_line, new_import_line)
    
    # Add handler registration
    handler_regex = r'(application\.add_handler\(CommandHandler\("status",\s*cmd_status\)\))'
    if re.search(handler_regex, main_content):
        main_content = re.sub(handler_regex, r'\1\n    application.add_handler(CommandHandler("ratchet", cmd_ratchet))', main_content)
    else:
        # Fallback: find the last add_handler(CommandHandler...)
        handlers = list(re.finditer(r'application\.add_handler\(CommandHandler\([^)]+\)\)', main_content))
        if handlers:
            last_handler = handlers[-1]
            insert_str = '\n    application.add_handler(CommandHandler("ratchet", cmd_ratchet))'
            main_content = main_content[:last_handler.end()] + insert_str + main_content[last_handler.end():]
            
    with open(main_path, 'w') as f:
        f.write(main_content)
    print("✅ Registered /ratchet handler in main.py")
else:
    print("ℹ️ /ratchet handler already registered in main.py")

print("\n🎉 Ratchet toggle fully restored!")
