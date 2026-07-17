import re

with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# Add a helper function to fetch real positions
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

# Insert helper before cmd_positions
if '_fetch_live_positions' not in content:
    content = content.replace('async def cmd_positions(', helper_func + '\nasync def cmd_positions(')

# Update cmd_positions to use live data
old_positions_func = r'async def cmd_positions\(update: Update, context: ContextTypes\.DEFAULT_TYPE\) -> None:.*?await update\.message\.reply_text\(msg, parse_mode="Markdown"\)'

new_positions_func = '''async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show live positions from Hyperliquid."""
    positions, balance = await _fetch_live_positions()
    
    if not positions:
        await update.message.reply_text("📭 No open positions")
        return
    
    total_notional = sum(p["notional"] for p in positions)
    total_pnl = 0.0  # Would need mark price to calculate
    
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

content = re.sub(old_positions_func, new_positions_func, content, flags=re.DOTALL)

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Telegram /positions command updated to show live data")
