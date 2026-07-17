import re

# 1. Read the file
with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# 2. Add the Live Fetcher Helper (if not already there)
helper = """
async def _fetch_live_positions():
    import requests, os
    try:
        addr = os.getenv("HL_ACCOUNT_ADDRESS")
        if not addr: return [], 0.0
        r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "userState", "user": addr}, timeout=10)
        if r.status_code != 200: return [], 0.0
        data = r.json()
        bal = float(data.get("marginSummary", {}).get("accountValue", 0))
        pos = []
        for p in data.get("assetPositions", []):
            pz = p.get("position", {})
            szi = float(pz.get("szi", 0))
            if abs(szi) > 0.0001:
                pos.append({"coin": pz.get("coin"), "size": abs(szi), "side": "long" if szi > 0 else "short", "entry": float(pz.get("entryPx", 0))})
        return pos, bal
    except Exception as e:
        print(f"API Error: {e}")
        return [], 0.0
"""

if '_fetch_live_positions' not in content:
    content += "\n" + helper

# 3. Fix the "80%" text to "500%"
content = content.replace("80% max", "500% max")

# 4. Replace the cmd_positions function body safely
start_idx = content.find("async def cmd_positions(")
if start_idx != -1:
    # Find the next function definition to know where this one ends
    next_def_idx = content.find("\nasync def ", start_idx + 10)
    if next_def_idx == -1:
        next_def_idx = len(content)
    
    # The new, working function
    new_func = """async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    positions, balance = await _fetch_live_positions()
    if not positions:
        await update.message.reply_text("📭 No open positions")
        return
    
    msg = " *Open Positions*\\n\\n"
    for p in positions:
        msg += f"🔹 *{p['coin']}* ({p['side'].upper()})\\n"
        msg += f"   Size: {p['size']}\\n"
        msg += f"   Entry: ${p['entry']:.4f}\\n\\n"
    
    msg += f"💰 *Balance:* ${balance:.2f}"
    await update.message.reply_text(msg, parse_mode="Markdown")
"""
    # Splice the new function in
    content = content[:start_idx] + new_func + content[next_def_idx:]

# 5. Save the file
with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Telegram bot patched successfully")
