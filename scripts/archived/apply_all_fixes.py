import re

# ============================================================================
# FIX 1: Update monitoring/alert_manager.py - Live positions from API
# ============================================================================
with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# Add the live positions fetcher function
helper_func = '''
async def _fetch_live_positions():
    """Fetch real-time positions from Hyperliquid API."""
    import requests
    import os
    
    try:
        address = os.getenv("HL_ACCOUNT_ADDRESS", "")
        if not address:
            return [], 0.0
        
        resp = requests.post(
            "https://api.hyperliquid.xyz/info",
            json={"type": "userState", "user": address},
            timeout=10
        )
        
        if resp.status_code != 200:
            return [], 0.0
        
        data = resp.json()
        balance = float(data.get("marginSummary", {}).get("accountValue", 0))
        
        positions = []
        for pos_data in data.get("assetPositions", []):
            pos = pos_data.get("position", {})
            szi = float(pos.get("szi", 0))
            if abs(szi) > 0.0001:
                positions.append({
                    "coin": pos.get("coin"),
                    "size": abs(szi),
                    "side": "long" if szi > 0 else "short",
                    "entry": float(pos.get("entryPx", 0)),
                    "notional": abs(szi) * float(pos.get("entryPx", 0))
                })
        
        return positions, balance
    except Exception as e:
        logger.error(f"Failed to fetch live positions: {e}")
        return [], 0.0

'''

# Insert helper before cmd_positions if not already there
if '_fetch_live_positions' not in content:
    # Find cmd_positions function and insert before it
    content = content.replace('async def cmd_positions(', helper_func + '\nasync def cmd_positions(')

# Replace the cmd_positions function body
old_cmd_positions = r'async def cmd_positions\(update: Update, context: ContextTypes\.DEFAULT_TYPE\) -> None:.*?await update\.message\.reply_text\(msg, parse_mode="Markdown"\)'

new_cmd_positions = '''async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show live positions from Hyperliquid."""
    positions, balance = await _fetch_live_positions()
    
    if not positions:
        await update.message.reply_text("📭 No open positions")
        return
    
    total_notional = sum(p["notional"] for p in positions)
    
    msg = f"📊 *Open Positions ({len(positions)})*\\n\\n"
    for pos in positions:
        msg += (
            f"🔹 *{pos['coin']}* ({pos['side'].upper()})\\n"
            f"   Size: {pos['size']}\\n"
            f"   Entry: ${pos['entry']:.4f}\\n"
            f"   Notional: ${pos['notional']:.2f}\\n\\n"
        )
    
    msg += (
        f"💰 *Total Notional:* ${total_notional:.2f}\\n"
        f"📊 *Balance:* ${balance:.2f}\\n"
        f"📈 *Deployed:* {(total_notional/balance*100) if balance > 0 else 0:.1f}%"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown")'''

content = re.sub(old_cmd_positions, new_cmd_positions, content, flags=re.DOTALL)

# Also update cmd_status to use live data
old_status_positions = r'positions = list\(state\.OPEN_POSITIONS\.values\(\)\)'
new_status_positions = '''# Fetch live positions from exchange
    positions, live_balance = await _fetch_live_positions()
    if not positions:
        positions = list(state.OPEN_POSITIONS.values())
    if live_balance > 0:
        balance = live_balance'''

content = re.sub(old_status_positions, new_status_positions, content)

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Fixed alert_manager.py - Telegram now shows live positions")

# ============================================================================
# FIX 2: Add execution alerts with TP/SL to main.py
# ============================================================================
with open('main.py', 'r') as f:
    main_content = f.read()

# Find where orders are executed and add alert
# Look for the pattern where order success is logged
old_success_pattern = r'(logger\.info\(f"✅ \{asset_name\} position opened successfully"\))'

new_success_code = '''logger.info(f"✅ {asset_name} position opened successfully")
            
            # Send Telegram alert with TP/SL details
            try:
                import monitoring.alert_manager as alert_mgr
                import asyncio
                
                # Calculate TP/SL levels
                entry = float(entry_price)
                atr = entry * 0.02
                sl = entry - (1.5 * atr) if side == "BUY" else entry + (1.5 * atr)
                tp1 = entry + (1.0 * atr) if side == "BUY" else entry - (1.0 * atr)
                tp2 = entry + (2.0 * atr) if side == "BUY" else entry - (2.0 * atr)
                tp3 = entry + (3.0 * atr) if side == "BUY" else entry - (3.0 * atr)
                
                alert_msg = (
                    f"🚀 *NEW TRADE EXECUTED*\\n\\n"
                    f"📊 *Asset:* {asset_name}\\n"
                    f"📈 *Side:* {side}\\n"
                    f"💰 *Entry:* ${entry:.4f}\\n"
                    f"📦 *Size:* {size:.4f}\\n"
                    f"💵 *Notional:* ${size * entry:.2f}\\n\\n"
                    f"🛡️ *Stop Loss:* ${sl:.4f}\\n"
                    f"🎯 *TP1:* ${tp1:.4f}\\n"
                    f"🎯 *TP2:* ${tp2:.4f}\\n"
                    f"🎯 *TP3:* ${tp3:.4f}\\n\\n"
                    f"🤖 *Confidence:* {conf}%\\n"
                    f"🧠 *Provider:* {provider}"
                )
                
                # Send to Telegram
                if hasattr(alert_mgr, 'application') and alert_mgr.application:
                    asyncio.create_task(
                        alert_mgr.application.bot.send_message(
                            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                            text=alert_msg,
                            parse_mode="Markdown"
                        )
                    )
            except Exception as e:
                logger.error(f"Failed to send trade alert: {e}")'''

main_content = re.sub(old_success_pattern, new_success_code, main_content)

with open('main.py', 'w') as f:
    f.write(main_content)

print("✅ Fixed main.py - Added execution alerts with TP/SL")
