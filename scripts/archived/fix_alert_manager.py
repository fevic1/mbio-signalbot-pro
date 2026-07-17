# Read the file
with open('monitoring/alert_manager.py', 'r') as f:
    content = f.read()

# Add the helper function at the top (after imports)
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

# Insert helper after the imports (find first 'async def' or 'def')
lines = content.split('\n')
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith('async def ') or line.startswith('def '):
        insert_idx = i
        break

lines.insert(insert_idx, helper_func)
content = '\n'.join(lines)

# Write back
with open('monitoring/alert_manager.py', 'w') as f:
    f.write(content)

print("✅ Helper function added")
