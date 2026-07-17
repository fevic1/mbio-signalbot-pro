with open('main.py', 'r') as f:
    content = f.read()

# 1. Fix the async crash in _sync_exchange_positions
old_sync = '''            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''
new_sync = '''            resp = await asyncio.to_thread(
                requests.post,
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''

if old_sync in content:
    content = content.replace(old_sync, new_sync)
    print("✅ Fixed async crash in sync function")
else:
    print("⚠️ Could not find exact sync pattern to fix")

# 2. Add state saving immediately after sync
if 'state.save_state()' not in content:
    content = content.replace(
        'logger.info(f"🔄 Synced {synced} position(s) from exchange")',
        'logger.info(f"🔄 Synced {synced} position(s) from exchange")\n            state.save_state()'
    )

# 3. Add a background state saver loop
saver_loop = '''
async def state_saver_loop():
    """Saves state to disk every 30 seconds."""
    while True:
        await asyncio.sleep(30)
        try:
            state.save_state()
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
'''

if 'async def state_saver_loop' not in content:
    content += saver_loop
    print("✅ Added background state saver")

# 4. Add the saver to the main asyncio.gather
old_gather = '''        await asyncio.gather(
            position_monitor_loop(TELEGRAM_CHAT_ID),'''
new_gather = '''        await asyncio.gather(
            state_saver_loop(),
            position_monitor_loop(TELEGRAM_CHAT_ID),'''

if old_gather in content:
    content = content.replace(old_gather, new_gather)
    print("✅ Added saver loop to main execution")

with open('main.py', 'w') as f:
    f.write(content)
