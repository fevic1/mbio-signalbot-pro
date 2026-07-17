with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# Find and replace the _fetch_live_positions function
old_helper_start = content.find('async def _fetch_live_positions():')
if old_helper_start == -1:
    print("❌ Helper function not found")
    exit(1)

# Find the next function definition
next_def = content.find('\nasync def ', old_helper_start + 10)
if next_def == -1:
    next_def = content.find('\ndef ', old_helper_start + 10)
if next_def == -1:
    next_def = len(content)

# New robust helper with retry logic
new_helper = '''async def _fetch_live_positions():
    """Fetch positions with retry logic and error handling."""
    import requests
    import os
    import time
    
    address = os.getenv("HL_ACCOUNT_ADDRESS")
    if not address:
        logger.error("❌ HL_ACCOUNT_ADDRESS not set")
        return [], 0.0
    
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "userState", "user": address},
                timeout=15
            )
            
            # Check for HTTP errors
            if resp.status_code != 200:
                logger.warning(f"⚠️ API returned {resp.status_code} - retry {attempt+1}/3")
                time.sleep(2 * (attempt + 1))
                continue
            
            # Check if response is actually JSON
            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"❌ Invalid JSON response: {resp.text[:100]}")
                time.sleep(2 * (attempt + 1))
                continue
            
            # Extract balance
            balance = float(data.get("marginSummary", {}).get("accountValue", 0))
            
            # Extract positions
            positions = []
            for p in data.get("assetPositions", []):
                pz = p.get("position", {})
                szi = float(pz.get("szi", 0))
                if abs(szi) > 0.0001:
                    positions.append({
                        "coin": pz.get("coin"),
                        "size": abs(szi),
                        "side": "long" if szi > 0 else "short",
                        "entry": float(pz.get("entryPx", 0))
                    })
            
            logger.info(f"✅ Fetched {len(positions)} positions from API")
            return positions, balance
            
        except Exception as e:
            logger.error(f"❌ API attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    
    logger.error("❌ All 3 API attempts failed")
    return [], 0.0

'''

# Replace the old helper
content = content[:old_helper_start] + new_helper + content[next_def:]

with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Added retry logic and error handling to API fetch")
