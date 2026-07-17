with open('main.py', 'r') as f:
    content = f.read()

# 1. Fix the async crash - wrap sync requests.post in asyncio.to_thread
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

if old_sync in content:
    content = content.replace(old_sync, new_sync)
    print("✅ Fixed async crash and API endpoint")
else:
    # Try alternate pattern
    if '"type": "userState"' in content:
        content = content.replace('"type": "userState"', '"type": "clearinghouseState"')
        print("✅ Fixed API endpoint")
    
    # Check if requests.post needs wrapping
    if 'resp = requests.post(' in content and 'await asyncio.to_thread' not in content:
        # Find the sync function and wrap it
        content = content.replace(
            'resp = requests.post(\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )',
            'resp = await asyncio.to_thread(\n                requests.post,\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )'
        )
        print("✅ Wrapped sync call in asyncio.to_thread")

# 2. Add state saver function BEFORE main()
saver_func = '''
async def state_saver_loop():
    """Saves state to disk every 30 seconds."""
    while True:
        await asyncio.sleep(30)
        try:
            state.save_state()
            logger.debug("💾 State saved")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

'''

if 'async def state_saver_loop' not in content:
    # Insert before async def main()
    content = content.replace('async def main()', saver_func + 'async def main()')
    print("✅ Added state_saver_loop function")

# 3. Add saver to asyncio.gather
if 'state_saver_loop()' not in content:
    content = content.replace(
        'await asyncio.gather(\n            position_monitor_loop',
        'await asyncio.gather(\n            state_saver_loop(),\n            position_monitor_loop'
    )
    print("✅ Added saver to main execution")

with open('main.py', 'w') as f:
    f.write(content)

print("✅ All fixes applied")
