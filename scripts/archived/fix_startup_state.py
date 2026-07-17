with open('main.py', 'r') as f:
    content = f.read()

# 1. Add load_state() call before _sync_exchange_positions()
old_startup = '''async def main() -> None:
    init_db()
    init_ai_clients()
    await _sync_exchange_positions()'''

new_startup = '''async def main() -> None:
    init_db()
    init_ai_clients()
    
    # Load persisted state from disk/Redis FIRST
    try:
        from core.state import load_state
        load_state()
        logger.info(f"✅ Loaded {len(state.OPEN_POSITIONS)} positions from persistence")
    except Exception as e:
        logger.error(f"⚠️ Failed to load state: {e}")
    
    # Then sync with exchange (adds new positions, preserves existing)
    await _sync_exchange_positions()'''

content = content.replace(old_startup, new_startup)

# 2. Fix the API endpoint to use clearinghouseState (the working one)
if '"type": "userState"' in content:
    content = content.replace('"type": "userState"', '"type": "clearinghouseState"')
    print("✅ Fixed API endpoint to clearinghouseState")

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Added state loading to startup sequence")
