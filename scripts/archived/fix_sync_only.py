with open('main.py', 'r') as f:
    content = f.read()

# ONLY fix the async crash - wrap requests.post in asyncio.to_thread
# Find the _sync_exchange_positions function and fix just the HTTP call
old_pattern = '''            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "userState", "user": address},
                timeout=15
            )'''

new_pattern = '''            resp = await asyncio.to_thread(
                requests.post,
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": address},
                timeout=15
            )'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Fixed async crash and API endpoint")
else:
    print("⚠️ Pattern not found, checking current state...")
    # Check what's there
    if 'userState' in content:
        content = content.replace('userState', 'clearinghouseState')
        print("✅ Fixed API endpoint only")
    
    if 'resp = requests.post(' in content and 'await asyncio.to_thread' not in content:
        # Need to wrap it
        import re
        # Find the sync function and wrap the requests.post call
        content = re.sub(
            r'resp = requests\.post\(\s*"https://api\.hyperliquid\.xyz/info",\s*json=\{"type": "clearinghouseState", "user": address\},\s*timeout=15\s*\)',
            'resp = await asyncio.to_thread(\n                requests.post,\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )',
            content
        )
        print("✅ Wrapped sync call")

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Minimal sync fix applied")
