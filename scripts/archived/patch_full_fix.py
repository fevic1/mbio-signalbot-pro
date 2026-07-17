import re

# ==============================================================================
# PATCH 1: Fix main.py (Position Sync via HTTP + Retries)
# ==============================================================================
with open('main.py', 'r') as f:
    main_content = f.read()

new_sync_func = """async def _sync_exchange_positions() -> None:
    \"\"\"Fetch live positions from Hyperliquid with retry logic via HTTP.\"\"\"
    import requests
    import time
    import core.state as state
    import os
    from datetime import datetime, timezone
    
    address = os.getenv("HL_ACCOUNT_ADDRESS", "")
    if not address:
        logger.warning("️ HL_ACCOUNT_ADDRESS missing — skipping exchange sync")
        return
    
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "userState", "user": address},
                timeout=15
            )
            if resp.status_code != 200:
                logger.warning(f"⚠️ API returned {resp.status_code} — retry {attempt+1}/3")
                time.sleep(5 * (attempt + 1))
                continue
            
            user_state = resp.json()
            asset_positions = user_state.get("assetPositions", [])
            synced = 0
            
            for pos_data in asset_positions:
                try:
                    if not isinstance(pos_data, dict): continue
                    pos = pos_data.get("position", {})
                    if not isinstance(pos, dict): continue
                    coin = pos.get("coin")
                    if not coin: continue
                    szi = float(pos.get("szi", 0) or 0)
                    entry = float(pos.get("entryPx", 0) or 0)
                    if abs(szi) < 0.0001 or coin in state.OPEN_POSITIONS: continue
                    
                    side = "BUY" if szi > 0 else "SELL"
                    size = abs(szi)
                    atr = entry * 0.02 if entry > 0 else 0.02
                    
                    if side == "BUY":
                        sl = entry - (1.5 * atr)
                        tp1, tp2, tp3 = entry + (1.0 * atr), entry + (2.0 * atr), entry + (3.0 * atr)
                    else:
                        sl = entry + (1.5 * atr)
                        tp1, tp2, tp3 = entry - (1.0 * atr), entry - (2.0 * atr), entry - (3.0 * atr)
                    
                    state.OPEN_POSITIONS[coin] = {
                        "side": side, "entry": entry, "size": size,
                        "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
                        "order_id": "synced_on_restart",
                        "opened_at": datetime.now(timezone.utc),
                    }
                    synced += 1
                    logger.info(f"🔄 Synced: {coin} {side} {size}")
                except Exception as e:
                    logger.error(f"⚠️ Sync error for position: {e}")
            
            logger.info(f"✅ Synced {synced} position(s) from exchange" if synced else "ℹ️ No positions to sync")
            return
        except Exception as e:
            logger.error(f"❌ Sync attempt {attempt+1} failed: {e}")
            if attempt < 2: time.sleep(5 * (attempt + 1))
    logger.error("❌ Failed to sync positions after 3 attempts")
"""

# Replace the old function
pattern = r'async def _sync_exchange_positions\(\) -> None:.*?(?=\nasync def |\nclass |\nif __name__|$)'
main_content = re.sub(pattern, new_sync_func, main_content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(main_content)
print("✅ Patched main.py (Position Sync)")

# ==============================================================================
# PATCH 2: Fix monitoring/alert_manager.py (Telegram Display)
# ==============================================================================
with open('monitoring/alert_manager.py', 'r') as f:
    alert_content = f.read()

# 1. Add HTTP fetcher helper
helper = """
async def _get_real_exchange_data() -> tuple[float, list]:
    import requests, os
    try:
        address = os.getenv("HL_ACCOUNT_ADDRESS", "")
        if not address: return 0.0, []
        resp = requests.post("https://api.hyperliquid.xyz/info", json={"type": "userState", "user": address}, timeout=10)
        if resp.status_code != 200: return 0.0, []
        data = resp.json()
        balance = float(data.get("marginSummary", {}).get("accountValue", 0))
        positions = []
        for pos_data in data.get("assetPositions", []):
            pos = pos_data.get("position", {})
            szi = float(pos.get("szi", 0))
            if abs(szi) > 0.0001:
                positions.append({"coin": pos.get("coin"), "size": abs(szi), "side": "long" if szi > 0 else "short", "entry": float(pos.get("entryPx", 0))})
        return balance, positions
    except Exception as e:
        logger.error(f"Failed to fetch real balance: {e}")
        return 0.0, []
"""

if '_get_real_exchange_data' not in alert_content:
    alert_content = alert_content.replace('async def cmd_status(', helper + '\nasync def cmd_status(')

# 2. Update cmd_status to use real data and 500% limit
# Find the balance assignment and replace it
old_balance = 'balance = get_account_balance()'
new_balance = '''balance, exchange_positions = await _get_real_exchange_data()
    if balance == 0:
        balance = get_account_balance()
        exchange_positions = list(state.OPEN_POSITIONS.values())
    positions = exchange_positions'''

alert_content = alert_content.replace(old_balance, new_balance)

# 3. Fix the hardcoded 80% limit
alert_content = alert_content.replace('80% max for NEW trades', '500% max for NEW trades')

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(alert_content)
print("✅ Patched alert_manager.py (Telegram Display)")
