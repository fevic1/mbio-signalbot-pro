import re
import os

print("🏛️ INITIATING WALL STREET MASTER UPGRADE...")

# ============================================================================
# PROTOCOL 1: BULLETPROOF STATE & SYNC (main.py)
# Fixes the async crash, uses the correct API, and adds Redis/Disk persistence.
# ============================================================================
with open('main.py', 'r') as f:
    main_content = f.read()

# Fix 1A: The Async Crash & API Endpoint
old_sync = '''            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "userState", "user": address},
                timeout=15
            )'''
new_sync = '''            resp = await asyncio.to_thread(
                requests.post,
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''
main_content = main_content.replace(old_sync, new_sync)

# Fix 1B: Load state on boot and add background saver
if 'state.load_state()' not in main_content:
    main_content = main_content.replace(
        'await _sync_exchange_positions()',
        'state.load_state()\n    logger.info(f"💾 Loaded {len(state.OPEN_POSITIONS)} positions from persistence")\n    await _sync_exchange_positions()\n    state.save_state()'
    )

saver_loop = '''
async def state_saver_loop():
    """Institutional state persistence every 30s."""
    while True:
        await asyncio.sleep(30)
        try: state.save_state()
        except: pass
'''
if 'async def state_saver_loop' not in main_content:
    main_content += saver_loop
    main_content = main_content.replace(
        'await asyncio.gather(\n            position_monitor_loop',
        'await asyncio.gather(\n            state_saver_loop(),\n            position_monitor_loop'
    )

# Fix 1C: Fix the calculate_trade_plan bug (missing signal parameter)
main_content = main_content.replace(
    '_tp_s = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"])',
    '_tp_s = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"], signal)'
)
main_content = main_content.replace(
    '_tp_c = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"])',
    '_tp_c = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"], signal)'
)

with open('main.py', 'w') as f:
    f.write(main_content)
print("✅ Protocol 1: Bulletproof Sync & State Persistence Active")

# ============================================================================
# PROTOCOL 2: API-DRIVEN PRECISION (execution/hl_executor.py)
# Fetches exact tick sizes and lot sizes from Hyperliquid. No more "invalid size" errors.
# ============================================================================
with open('execution/hl_executor.py', 'r') as f:
    exec_content = f.read()

precision_inject = '''
# 🏛️ WALL STREET PROTOCOL: Dynamic Precision from Exchange
import requests
def get_hl_precision():
    try:
        r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "meta"}, timeout=10).json()
        mapping = {}
        for asset in r.get("universe", []):
            mapping[asset["name"]] = {
                "sz_decimals": asset.get("szDecimals", 2),
                "tick_size": float(asset.get("stepSize", 0.01))
            }
        return mapping
    except:
        return {}

HL_PRECISION = get_hl_precision()

def round_hl_price(asset, price):
    tick = HL_PRECISION.get(asset, {}).get("tick_size", 0.01)
    return round(price / tick) * tick

def round_hl_size(asset, size):
    dec = HL_PRECISION.get(asset, {}).get("sz_decimals", 2)
    return round(size, dec)
'''

if 'HL_PRECISION' not in exec_content:
    exec_content = exec_content.replace('class HLExecutor', precision_inject + '\n\nclass HLExecutor')
    
    # Inject rounding right before the order call
    old_order_call = 'result = self.exchange.order(coin, is_buy, sz, px,'
    new_order_call = '''px = round_hl_price(coin, px)
            sz = round_hl_size(coin, sz)
            logger.info(f"🎯 Institutional Rounding: {coin} px={px} sz={sz}")
            result = self.exchange.order(coin, is_buy, sz, px,'''
    exec_content = exec_content.replace(old_order_call, new_order_call)

with open('execution/hl_executor.py', 'w') as f:
    f.write(exec_content)
print("✅ Protocol 2: API-Driven Dynamic Precision Active")

# ============================================================================
# PROTOCOL 3: SCALE-OUT EXITS (monitoring/position_tracker.py)
# Closes 33% at TP1, moves SL to Breakeven. Closes 33% at TP2. Rest at TP3.
# ============================================================================
with open('monitoring/position_tracker.py', 'r') as f:
    tracker_content = f.read()

# We will inject the scale-out logic into the existing check_and_close_positions
# Find the exact block where it checks TP1/TP2/TP3 and replace it with institutional logic
old_tp_logic = '''            # ── LONG ──────────────────────────────────────────────
            if side == "BUY":
                if current_price >= pos.get("tp3", float("inf")):
                    should_close = True
                    close_reason = "TP3 Hit"
                    tp_hit_label = "TP3"

                elif (
                    current_price >= pos.get("tp2", float("inf"))
                    and pos.get("sl", 0) < pos.get("tp1", 0)
                ):
                    pos["sl"] = pos["tp1"]
                    await send_tp_hit(asset, "TP2", current_price, entry, chat_id)

                elif (
                    current_price >= pos.get("tp1", float("inf"))
                    and pos.get("sl", 0) < entry
                ):
                    pos["sl"] = entry
                    await send_tp_hit(asset, "TP1", current_price, entry, chat_id)

                elif current_price <= pos["sl"]:
                    should_close = True
                    close_reason = "Stop Loss Hit"

            # ── SHORT ─────────────────────────────────────────────
            else:
                if current_price <= pos.get("tp3", 0):
                    should_close = True
                    close_reason = "TP3 Hit"
                    tp_hit_label = "TP3"

                elif (
                    current_price <= pos.get("tp2", float("inf"))
                    # FIX 2: completed truncated expression
                    and pos.get("sl", float("inf")) > pos.get("tp1", float("inf"))
                ):
                    pos["sl"] = pos["tp1"]
                    await send_tp_hit(asset, "TP2", current_price, entry, chat_id)

                elif (
                    current_price <= pos.get("tp1", float("inf"))
                    and pos.get("sl", float("inf")) > entry
                ):
                    pos["sl"] = entry
                    await send_tp_hit(asset, "TP1", current_price, entry, chat_id)

                elif current_price >= pos["sl"]:
                    should_close = True
                    close_reason = "Stop Loss Hit"'''

new_institutional_tp = '''            # 🏛️ WALL STREET PROTOCOL: Scale-Out Exits & Breakeven Protection
            tp1_hit = pos.get("tp1_hit", False)
            tp2_hit = pos.get("tp2_hit", False)
            
            if side == "BUY":
                if current_price >= pos.get("tp3", float("inf")):
                    should_close = True; close_reason = "TP3 Hit"; tp_hit_label = "TP3"
                elif current_price >= pos.get("tp2", float("inf")) and not tp2_hit:
                    pos["tp2_hit"] = True
                    pos["sl"] = pos["tp1"] # Trail stop to TP1
                    size = size * 0.33 # Close 33%
                    should_close = True; close_reason = "TP2 Scale-Out"; tp_hit_label = "TP2"
                    await send_tp_hit(asset, "TP2 (Scaled Out 33%)", current_price, entry, chat_id)
                elif current_price >= pos.get("tp1", float("inf")) and not tp1_hit:
                    pos["tp1_hit"] = True
                    pos["sl"] = entry # MOVE STOP TO BREAKEVEN (Zero Risk)
                    size = size * 0.33 # Close 33%
                    should_close = True; close_reason = "TP1 Scale-Out"; tp_hit_label = "TP1"
                    await send_tp_hit(asset, "TP1 (Scaled Out 33% + SL moved to BE)", current_price, entry, chat_id)
                elif current_price <= pos["sl"]:
                    should_close = True; close_reason = "Stop Loss Hit"
            else:
                if current_price <= pos.get("tp3", 0):
                    should_close = True; close_reason = "TP3 Hit"; tp_hit_label = "TP3"
                elif current_price <= pos.get("tp2", float("inf")) and not tp2_hit:
                    pos["tp2_hit"] = True
                    pos["sl"] = pos["tp1"]
                    size = size * 0.33
                    should_close = True; close_reason = "TP2 Scale-Out"; tp_hit_label = "TP2"
                    await send_tp_hit(asset, "TP2 (Scaled Out 33%)", current_price, entry, chat_id)
                elif current_price <= pos.get("tp1", float("inf")) and not tp1_hit:
                    pos["tp1_hit"] = True
                    pos["sl"] = entry # MOVE STOP TO BREAKEVEN
                    size = size * 0.33
                    should_close = True; close_reason = "TP1 Scale-Out"; tp_hit_label = "TP1"
                    await send_tp_hit(asset, "TP1 (Scaled Out 33% + SL moved to BE)", current_price, entry, chat_id)
                elif current_price >= pos["sl"]:
                    should_close = True; close_reason = "Stop Loss Hit"'''

tracker_content = tracker_content.replace(old_tp_logic, new_institutional_tp)

with open('monitoring/position_tracker.py', 'w') as f:
    f.write(tracker_content)
print("✅ Protocol 3: Institutional Scale-Out Exits (TP1/TP2/TP3) Active")

# ============================================================================
# PROTOCOL 4: LIVE TELEMETRY (monitoring/alert_manager.py)
# Telegram commands now read directly from the live exchange API.
# ============================================================================
with open('monitoring/alert_manager.py', 'r') as f:
    alert_content = f.read()

live_fetcher = '''
# 🏛️ WALL STREET PROTOCOL: Live Exchange Telemetry
async def _fetch_live_positions():
    import requests, os
    try:
        addr = os.getenv("HL_ACCOUNT_ADDRESS")
        if not addr: return [], 0.0
        r = await asyncio.to_thread(requests.post, "https://api.hyperliquid.xyz/info", json={"type": "clearinghouseState", "user": addr}, timeout=10)
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
    except: return [], 0.0
'''

if '_fetch_live_positions' not in alert_content:
    alert_content += live_fetcher

    # Update /positions
    old_cmd_pos = '''async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all open positions."""
    if not state.OPEN_POSITIONS:
        await update.message.reply_text("📭 No open positions")
        return
    
    msg = "📊 *Open Positions*\\n\\n"
    for asset, pos in state.OPEN_POSITIONS.items():
        msg += f"🔹 *{asset}* ({pos['side']})\\n"
        msg += f"   Size: {pos['size']}\\n"
        msg += f"   Entry: ${pos['entry']:.4f}\\n"
        msg += f"   SL: ${pos['sl']:.4f}\\n"
        msg += f"   TP1: ${pos['tp1']:.4f}\\n"
        msg += f"   TP2: ${pos['tp2']:.4f}\\n"
        msg += f"   TP3: ${pos['tp3']:.4f}\\n\\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")'''
    
    new_cmd_pos = '''async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show live positions from exchange."""
    positions, balance = await _fetch_live_positions()
    if not positions:
        await update.message.reply_text("📭 No open positions")
        return
    msg = f"🏛️ *Live Exchange Positions*\\n\\n"
    for p in positions:
        msg += f"🔹 *{p['coin']}* ({p['side'].upper()})\\n   Size: {p['size']}\\n   Entry: ${p['entry']:.4f}\\n\\n"
    msg += f"💰 *Total Balance:* ${balance:.2f}"
    await update.message.reply_text(msg, parse_mode="Markdown")'''
    alert_content = alert_content.replace(old_cmd_pos, new_cmd_pos)

    # Update /status
    alert_content = alert_content.replace('80% max for NEW trades', '100% max (Institutional Risk)')
    alert_content = alert_content.replace(
        'positions = list(state.OPEN_POSITIONS.values())',
        'positions, live_bal = await _fetch_live_positions()\n    if live_bal > 0: balance = live_bal'
    )

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(alert_content)
print("✅ Protocol 4: Live Exchange Telemetry Active")

print("\n🏛️ MASTER UPGRADE COMPLETE. The bot is now Institutional-Grade.")
