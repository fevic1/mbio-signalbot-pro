with open('main.py', 'r') as f:
    content = f.read()

# Find the _sync_exchange_positions function and fix the async issue
# The problem is that requests.post() is sync but the function is async

old_sync_start = '''async def _sync_exchange_positions() -> None:
    """Fetch live positions from Hyperliquid with retry logic via HTTP."""
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
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''

new_sync_start = '''async def _sync_exchange_positions() -> None:
    """Fetch live positions from Hyperliquid with retry logic via HTTP."""
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
            # Wrap sync HTTP call in asyncio.to_thread
            resp = await asyncio.to_thread(
                requests.post,
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''

if old_sync_start in content:
    content = content.replace(old_sync_start, new_sync_start)
    print("✅ Fixed async/sync mismatch in _sync_exchange_positions")
else:
    print("⚠️ Could not find exact pattern, trying alternative fix")
    # Try a simpler replacement
    content = content.replace(
        'resp = requests.post(\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )',
        'resp = await asyncio.to_thread(\n                requests.post,\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )'
    )

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Applied async fix")
